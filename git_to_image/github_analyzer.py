# git_to_image/github_analyzer.py
# Module for all GitHub API interactions
import os
import json
from datetime import datetime, timedelta
from collections import Counter
from github import Github, GithubException
from google import genai
import re

# --- Domain Analysis ---
# The list of domains we will ask Gemini to classify repositories into.
DOMAIN_LIST = [
    "AI/ML", "Web Frontend", "Web Backend", "Game Development", 
    "Data Science", "DevOps/Infra", "Mobile", "Cybersecurity"
]

# --- High-Profile Framework Detection ---
HIGH_PROFILE_FRAMEWORKS = {
    # AI/ML Frameworks
    'pytorch': {'category': 'AI/ML', 'impact': 'legendary', 'type': 'deep_learning'},
    'tensorflow': {'category': 'AI/ML', 'impact': 'legendary', 'type': 'deep_learning'},
    'scikit-learn': {'category': 'AI/ML', 'impact': 'legendary', 'type': 'machine_learning'},
    'xgboost': {'category': 'AI/ML', 'impact': 'high', 'type': 'machine_learning'},
    'pandas': {'category': 'Data Science', 'impact': 'legendary', 'type': 'data_processing'},
    'numpy': {'category': 'Data Science', 'impact': 'legendary', 'type': 'numerical_computing'},
    'tvm': {'category': 'AI/ML', 'impact': 'high', 'type': 'compiler_optimization'},
    
    # Web Frameworks
    'react': {'category': 'Web Frontend', 'impact': 'legendary', 'type': 'ui_framework'},
    'vue': {'category': 'Web Frontend', 'impact': 'legendary', 'type': 'ui_framework'},
    'angular': {'category': 'Web Frontend', 'impact': 'legendary', 'type': 'ui_framework'},
    'django': {'category': 'Web Backend', 'impact': 'legendary', 'type': 'web_framework'},
    'flask': {'category': 'Web Backend', 'impact': 'high', 'type': 'web_framework'},
    'nodejs': {'category': 'Web Backend', 'impact': 'legendary', 'type': 'runtime'},
    
    # System Level
    'linux': {'category': 'Operating Systems', 'impact': 'legendary', 'type': 'kernel'},
    'git': {'category': 'DevOps/Infra', 'impact': 'legendary', 'type': 'version_control'},
    'kubernetes': {'category': 'DevOps/Infra', 'impact': 'legendary', 'type': 'orchestration'},
    'docker': {'category': 'DevOps/Infra', 'impact': 'legendary', 'type': 'containerization'},
    
    # Programming Languages
    'rust': {'category': 'Systems Programming', 'impact': 'high', 'type': 'language'},
    'golang': {'category': 'Systems Programming', 'impact': 'high', 'type': 'language'},
    'typescript': {'category': 'Web Development', 'impact': 'high', 'type': 'language'},
}

def get_language_distribution(user, days_window=90):
    """
    Analyzes the language distribution for a user's repositories updated within the time window.
    """
    language_bytes = Counter()
    time_window_start = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days_window)
    
    for repo in user.get_repos(sort="updated"):
        # Convert repo.updated_at to naive datetime for comparison
        repo_updated = repo.updated_at.replace(tzinfo=None) if repo.updated_at.tzinfo else repo.updated_at
        
        if repo_updated < time_window_start:
            break # Repos are sorted by updated, so we can stop here
        
        # get_languages() can be expensive, but it's the most accurate way
        for lang, byte_count in repo.get_languages().items():
            language_bytes[lang] += byte_count

    total_bytes = sum(language_bytes.values())
    if total_bytes == 0:
        return {}

    return {lang: (count / total_bytes) * 100 for lang, count in language_bytes.items()}

def get_area_of_focus(user, gemini_client, days_window=90):
    """
    Analyzes repository READMEs using Gemini to determine primary areas of focus.
    Returns tuple: (domains, debug_info)
    """
    domain_counter = Counter()
    time_window_start = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days_window)
    
    # Debug tracking
    debug_info = {
        'gemini_calls': 0,
        'total_tokens': 0,
        'estimated_cost': 0.0,
        'repos_analyzed': 0,
        'readmes_processed': 0
    }

    # Create the prompt for Gemini
    prompt = f"Analyze the following README file content and classify its primary technical domain. Choose ONLY ONE from this list: {', '.join(DOMAIN_LIST)}. If no domain from the list is a good fit, respond with 'Other'."

    for repo in user.get_repos(sort="updated"):
        # Convert repo.updated_at to naive datetime for comparison
        repo_updated = repo.updated_at.replace(tzinfo=None) if repo.updated_at.tzinfo else repo.updated_at
        
        if repo_updated < time_window_start:
            break
            
        debug_info['repos_analyzed'] += 1
        
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode('utf-8')
            debug_info['readmes_processed'] += 1
            
            # To save on tokens and time, we'll only use the first ~1500 characters
            truncated_content = readme_content[:1500]

            full_prompt = f"{prompt}\n\nREADME CONTENT:\n---\n{truncated_content}"
            
            print(f"🤖 Analyzing {repo.full_name} with Gemini...")
            
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=full_prompt,
            )
            
            debug_info['gemini_calls'] += 1
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            input_tokens = len(full_prompt) // 4
            output_tokens = len(response.candidates[0].content.parts[0].text) // 4
            total_tokens = input_tokens + output_tokens
            debug_info['total_tokens'] += total_tokens
            
            # Estimate cost (Gemini 2.5 Flash pricing: ~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens)
            input_cost = (input_tokens / 1_000_000) * 0.075
            output_cost = (output_tokens / 1_000_000) * 0.30
            debug_info['estimated_cost'] += input_cost + output_cost
            
            print(f"   📊 Tokens: {total_tokens} (${(input_cost + output_cost):.6f})")
            
            # Clean up the response from Gemini
            domain = response.candidates[0].content.parts[0].text.strip()
            if domain in DOMAIN_LIST:
                domain_counter[domain] += 1
                print(f"   ✅ Classified as: {domain}")
            else:
                print(f"   ⚠️  Unrecognized domain: {domain}")

        except GithubException:
            # This repo might not have a README, which is fine.
            print(f"   ℹ️  No README found for {repo.full_name}")
            continue
        except Exception as e:
            # Catch potential errors from the Gemini API
            print(f"   ❌ Could not analyze repo {repo.full_name}: {e}")
            continue

    domains = [domain for domain, count in domain_counter.most_common(3)]
    return domains, debug_info

def get_contribution_style(user, days_window=90):
    """
    Analyzes the user's contribution patterns to determine their coding style.
    """
    time_window_start = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days_window)
    
    # Metrics to track
    total_commits = 0
    total_repos = 0
    own_repos = 0
    fork_repos = 0
    commit_sizes = []
    commit_messages = []
    
    for repo in user.get_repos(sort="updated"):
        repo_updated = repo.updated_at.replace(tzinfo=None) if repo.updated_at.tzinfo else repo.updated_at
        if repo_updated < time_window_start:
            break
            
        total_repos += 1
        if repo.owner.login == user.login:
            own_repos += 1
        if repo.fork:
            fork_repos += 1
            
        try:
            # Get recent commits in this repo
            commits = list(repo.get_commits(author=user, since=time_window_start))
            total_commits += len(commits)
            
            for commit in commits[:10]:  # Analyze up to 10 recent commits per repo
                # Analyze commit message
                commit_messages.append(commit.commit.message)
                
                # Analyze commit size (files changed)
                try:
                    files_changed = len(commit.files) if commit.files else 0
                    commit_sizes.append(files_changed)
                except:
                    pass  # Some commits might not have file info
                    
        except Exception as e:
            # Skip repos we can't access
            continue
    
    # Analyze commit message patterns
    avg_msg_length = sum(len(msg) for msg in commit_messages) / max(len(commit_messages), 1)
    has_conventional_commits = sum(1 for msg in commit_messages if re.match(r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: ', msg.lower())) / max(len(commit_messages), 1)
    
    # Analyze commit sizes
    avg_commit_size = sum(commit_sizes) / max(len(commit_sizes), 1)
    
    # Determine contribution style
    style_scores = {}
    
    # Solo Creator: Mostly own repos, fewer forks
    solo_score = (own_repos / max(total_repos, 1)) * 0.7 + (1 - fork_repos / max(total_repos, 1)) * 0.3
    style_scores["Solo Creator"] = solo_score
    
    # Collaborator: Many forks and contributions to others' repos
    collaborator_score = (fork_repos / max(total_repos, 1)) * 0.6 + min(total_commits / 50, 1) * 0.4
    style_scores["Collaborator"] = collaborator_score
    
    # Architect: Large commits, detailed messages, conventional commits
    architect_score = (min(avg_commit_size / 5, 1) * 0.4 + 
                      min(avg_msg_length / 50, 1) * 0.3 + 
                      has_conventional_commits * 0.3)
    style_scores["Architect"] = architect_score
    
    # Refined Developer: High conventional commit usage, moderate commit sizes
    refined_score = has_conventional_commits * 0.6 + (1 - abs(avg_commit_size - 3) / 10) * 0.4
    style_scores["Refined Developer"] = refined_score
    
    # Determine primary style
    primary_style = max(style_scores, key=style_scores.get)
    
    return {
        "primary_style": primary_style,
        "style_scores": style_scores,
        "metrics": {
            "total_commits": total_commits,
            "total_repos": total_repos,
            "own_repos": own_repos,
            "fork_repos": fork_repos,
            "avg_commit_size": round(avg_commit_size, 1),
            "avg_msg_length": round(avg_msg_length, 1),
            "conventional_commits_ratio": round(has_conventional_commits, 2)
        }
    }

def get_commit_cadence(user, repo_names, days_window=90):
    """
    Analyze commit frequency and patterns for calculating contribution consistency.
    
    Args:
        user: GitHub user object
        repo_names: List of repository names
        days_window: Days to analyze (default 90)
    
    Returns:
        dict: Commit cadence metrics including frequency and consistency
    """
    time_window_start = datetime.utcnow().replace(tzinfo=None) - timedelta(days=days_window)
    daily_commits = {}
    total_commits = 0
    
    for repo in user.get_repos():
        if repo.name not in repo_names:
            continue
            
        try:
            commits = list(repo.get_commits(author=user, since=time_window_start))
            total_commits += len(commits)
            
            for commit in commits:
                commit_date = commit.commit.author.date.date()
                daily_commits[commit_date] = daily_commits.get(commit_date, 0) + 1
                
        except Exception:
            continue
    
    if not daily_commits:
        return {"frequency": 0, "consistency": 0, "total_commits": 0}
    
    # Calculate frequency (commits per day on average)
    active_days = len(daily_commits)
    frequency = total_commits / days_window
    
    # Calculate consistency (how evenly distributed commits are)
    if active_days > 1:
        commit_counts = list(daily_commits.values())
        mean_daily = sum(commit_counts) / len(commit_counts)
        variance = sum((x - mean_daily) ** 2 for x in commit_counts) / len(commit_counts)
        consistency = 1 / (1 + variance)  # Higher consistency = lower variance
    else:
        consistency = 0.5 if total_commits > 0 else 0
    
    return {
        "frequency": round(frequency, 3),
        "consistency": round(consistency, 3),
        "total_commits": total_commits,
        "active_days": active_days
    }

def get_readme_content(repo):
    """
    Helper function to get README content from a repository.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        str: README content or empty string if not found
    """
    try:
        readme = repo.get_readme()
        content = readme.decoded_content.decode('utf-8')
        return content
    except:
        try:
            # Try different README file names
            for readme_name in ['README.md', 'readme.md', 'README.txt', 'readme.txt', 'README']:
                try:
                    file = repo.get_contents(readme_name)
                    return file.decoded_content.decode('utf-8')
                except:
                    continue
        except:
            pass
    return ""


def detect_high_profile_contributions(user, days_window=90):
    """
    Detect if user has contributed to high-profile open source frameworks.
    
    Args:
        user: GitHub user object
        days_window: Days to analyze (default 90)
    
    Returns:
        dict: High-profile contribution analysis
    """
    high_profile_contributions = {}
    total_impact_score = 0
    
    try:
        repos = user.get_repos()
        
        for repo in repos:
            repo_name = repo.name.lower()
            
            # Check if this repo matches any high-profile framework
            for framework, details in HIGH_PROFILE_FRAMEWORKS.items():
                if framework in repo_name or repo_name in framework:
                    # Calculate contribution significance
                    impact_multiplier = {
                        'legendary': 10,
                        'high': 5,
                        'medium': 2
                    }.get(details['impact'], 1)
                    
                    # Factor in repository metrics
                    stars = repo.stargazers_count
                    forks = repo.forks_count
                    
                    # Calculate final impact score
                    repo_impact = impact_multiplier * (1 + (stars / 1000) + (forks / 100))
                    
                    high_profile_contributions[framework] = {
                        'repo_name': repo.name,
                        'category': details['category'],
                        'type': details['type'],
                        'impact_level': details['impact'],
                        'stars': stars,
                        'forks': forks,
                        'impact_score': repo_impact,
                        'is_owner': repo.owner.login == user.login
                    }
                    
                    total_impact_score += repo_impact
                    break
    
    except Exception as e:
        print(f"⚠️ Error detecting high-profile contributions: {e}")
    
    return {
        'contributions': high_profile_contributions,
        'total_impact_score': total_impact_score,
        'legendary_count': sum(1 for c in high_profile_contributions.values() if c['impact_level'] == 'legendary'),
        'high_count': sum(1 for c in high_profile_contributions.values() if c['impact_level'] == 'high')
    }


def analyze_code_originality(user, days_window=90):
    """
    Analyze repository ownership patterns and code originality.
    
    Args:
        user: GitHub user object
        days_window: Days to look back for analysis
    
    Returns:
        dict: Originality analysis results
    """
    cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(days=days_window)
    
    owned_repos = 0
    forked_repos = 0
    contributed_repos = 0
    created_from_scratch = 0
    total_owned_stars = 0
    total_owned_forks = 0
    
    try:
        repos = user.get_repos()
        
        for repo in repos:
            # Handle timezone-aware datetime comparison
            repo_updated = repo.updated_at
            if repo_updated.tzinfo:
                repo_updated = repo_updated.replace(tzinfo=None)
            
            if repo_updated < cutoff_date:
                continue
                
            if repo.owner.login == user.login:
                owned_repos += 1
                total_owned_stars += repo.stargazers_count
                total_owned_forks += repo.forks_count
                
                if not repo.fork:
                    created_from_scratch += 1
                else:
                    forked_repos += 1
            else:
                contributed_repos += 1
    
    except Exception as e:
        print(f"⚠️ Error analyzing code originality: {e}")
        return {}
    
    # Calculate originality scores
    total_repos = owned_repos + contributed_repos
    if total_repos == 0:
        return {}
    
    originality_score = created_from_scratch / max(total_repos, 1)
    ownership_ratio = owned_repos / max(total_repos, 1)
    impact_score = (total_owned_stars + total_owned_forks * 2) / max(owned_repos, 1)
    
    # Classify creator type
    if originality_score > 0.7 and ownership_ratio > 0.6:
        creator_type = "Visionary Founder"
    elif originality_score > 0.4 and ownership_ratio > 0.4:
        creator_type = "Project Creator"
    elif ownership_ratio > 0.6:
        creator_type = "Repository Owner"
    elif contributed_repos > owned_repos * 2:
        creator_type = "Community Contributor"
    else:
        creator_type = "Balanced Developer"
    
    return {
        'creator_type': creator_type,
        'owned_repos': owned_repos,
        'forked_repos': forked_repos,
        'contributed_repos': contributed_repos,
        'created_from_scratch': created_from_scratch,
        'originality_score': originality_score,
        'ownership_ratio': ownership_ratio,
        'impact_score': impact_score,
        'total_owned_stars': total_owned_stars,
        'total_owned_forks': total_owned_forks
    }


def classify_frontend_backend_focus(user, gemini_client, days_window=90):
    """
    Use Gemini to classify repositories as frontend, backend, or full-stack focused.
    
    Args:
        user: GitHub user object
        gemini_client: Configured Gemini client
        days_window: Days to look back for analysis
    
    Returns:
        dict: Frontend/backend classification results
    """
    cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(days=days_window)
    
    frontend_score = 0
    backend_score = 0
    fullstack_score = 0
    total_analyzed = 0
    
    try:
        repos = user.get_repos()
        analyzed_repos = []
        
        for repo in repos:
            # Ensure timezone-naive comparison
            repo_updated = repo.updated_at.replace(tzinfo=None) if repo.updated_at.tzinfo else repo.updated_at
            if repo_updated < cutoff_date or repo.size == 0:
                continue
            
            # Skip if already analyzed enough repos (cost optimization)
            if total_analyzed >= 10:
                break
            
            try:
                readme_content = get_readme_content(repo)
                if not readme_content:
                    continue
                
                # Ask Gemini to classify the repository focus
                prompt = f"""
                Analyze this GitHub repository and classify it as Frontend, Backend, or Full-stack focused.
                
                Repository: {repo.name}
                Description: {repo.description or 'No description'}
                Primary Language: {repo.language or 'Unknown'}
                README Content: {readme_content[:1000]}...
                
                Respond with exactly one of: Frontend, Backend, Full-stack
                
                Classification criteria:
                - Frontend: UI libraries, web interfaces, mobile apps, design systems, client-side frameworks
                - Backend: APIs, servers, databases, microservices, infrastructure, algorithms, CLI tools
                - Full-stack: Projects that span both frontend and backend, complete applications
                """
                
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=prompt,
                )
                classification = response.text.strip()
                
                print(f"🤖 Analyzing {repo.name} focus...")
                print(f"   ✅ Classified as: {classification}")
                
                analyzed_repos.append({
                    'name': repo.name,
                    'classification': classification,
                    'language': repo.language,
                    'stars': repo.stargazers_count
                })
                
                # Weight by repository popularity
                weight = 1 + (repo.stargazers_count / 100)
                
                if 'Frontend' in classification:
                    frontend_score += weight
                elif 'Backend' in classification:
                    backend_score += weight
                elif 'Full-stack' in classification:
                    fullstack_score += weight
                
                total_analyzed += 1
                
            except Exception as e:
                print(f"⚠️ Error analyzing {repo.name}: {e}")
                continue
    
    except Exception as e:
        print(f"⚠️ Error in frontend/backend classification: {e}")
        return {}
    
    if total_analyzed == 0:
        return {}
    
    # Determine primary focus
    total_score = frontend_score + backend_score + fullstack_score
    if total_score == 0:
        return {}
    
    frontend_ratio = frontend_score / total_score
    backend_ratio = backend_score / total_score
    fullstack_ratio = fullstack_score / total_score
    
    if frontend_ratio > 0.5:
        primary_focus = "Frontend"
    elif backend_ratio > 0.5:
        primary_focus = "Backend"
    elif fullstack_ratio > 0.3:
        primary_focus = "Full-stack"
    elif frontend_ratio > backend_ratio:
        primary_focus = "Frontend-leaning"
    else:
        primary_focus = "Backend-leaning"
    
    return {
        'primary_focus': primary_focus,
        'frontend_score': frontend_score,
        'backend_score': backend_score,
        'fullstack_score': fullstack_score,
        'frontend_ratio': frontend_ratio,
        'backend_ratio': backend_ratio,
        'fullstack_ratio': fullstack_ratio,
        'analyzed_repos': analyzed_repos,
        'total_analyzed': total_analyzed
    }


# =============================================================================
# PHASE 3: Deep Collaboration & Code Style Analysis
# =============================================================================

def analyze_pull_requests(user, days_window=90):
    """
    Analyze PR activity for contribution type and collaboration style.
    
    Args:
        user: GitHub user object
        days_window: Number of days to look back
        
    Returns:
        dict: Collaboration profile with contribution types and patterns
    """
    print("🔍 Analyzing Pull Request patterns...")
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_window)
    
    collaboration_profile = {
        'total_prs_created': 0,
        'total_prs_reviewed': 0,
        'contribution_types': {'feature': 0, 'fix': 0, 'docs': 0, 'test': 0, 'other': 0},
        'collaboration_style': {'mentorship_score': 0, 'leadership_score': 0},
        'impact_metrics': {'total_additions': 0, 'total_deletions': 0, 'avg_pr_size': 0},
        'archetype_indicators': []
    }
    
    try:
        # Get user's repositories for PR analysis
        repos = list(user.get_repos(type='all', sort='updated'))[:20]  # Limit to avoid rate limits
        
        for repo in repos:
            try:
                # Analyze PRs created by the user
                user_prs = []
                all_prs = list(repo.get_pulls(state='all', sort='updated'))[:20]
                
                for pr in all_prs:
                    if pr.user.login == user.login and pr.created_at >= start_date:
                        user_prs.append(pr)
                        if len(user_prs) >= 10:  # Limit to recent PRs
                            break
                
                for pr in user_prs[:10]:  # Limit to recent PRs
                    collaboration_profile['total_prs_created'] += 1
                    
                    # Classify PR type based on title and files
                    pr_type = classify_pr_type(pr)
                    collaboration_profile['contribution_types'][pr_type] += 1
                    
                    # Track impact metrics
                    if pr.additions:
                        collaboration_profile['impact_metrics']['total_additions'] += pr.additions
                    if pr.deletions:
                        collaboration_profile['impact_metrics']['total_deletions'] += pr.deletions
                
                # Analyze PR reviews by the user (leadership/mentorship indicators)
                try:
                    recent_prs = list(repo.get_pulls(state='all', sort='updated'))[:10]
                    
                    for pr in recent_prs:
                        if pr.created_at >= start_date:
                            user_reviews = []
                            all_reviews = list(pr.get_reviews())
                            for review in all_reviews:
                                if review.user.login == user.login:
                                    user_reviews.append(review)
                            
                            if user_reviews:
                                collaboration_profile['total_prs_reviewed'] += 1
                                
                                # Analyze review quality for mentorship indicators
                                for review in user_reviews:
                                    if review.body and len(review.body) > 100:  # Substantial review
                                        collaboration_profile['collaboration_style']['mentorship_score'] += 1
                                    
                                    if review.state == 'APPROVED':
                                        collaboration_profile['collaboration_style']['leadership_score'] += 1
                                        
                except Exception:
                    continue  # Skip if reviews can't be accessed
                    
            except Exception:
                continue  # Skip problematic repos
    
    except Exception as e:
        print(f"   ⚠️ Limited PR analysis due to API constraints: {str(e)[:50]}...")
    
    # Calculate derived metrics
    total_changes = collaboration_profile['impact_metrics']['total_additions'] + \
                   collaboration_profile['impact_metrics']['total_deletions']
    
    if collaboration_profile['total_prs_created'] > 0:
        collaboration_profile['impact_metrics']['avg_pr_size'] = \
            total_changes / collaboration_profile['total_prs_created']
    
    # Determine archetype indicators
    archetype_indicators = []
    
    # Feature creator archetype
    if collaboration_profile['contribution_types']['feature'] > 2:
        archetype_indicators.append('feature_creator')
    
    # Bug fixer archetype  
    if collaboration_profile['contribution_types']['fix'] > collaboration_profile['contribution_types']['feature']:
        archetype_indicators.append('bug_fixer')
    
    # Documentation writer archetype
    if collaboration_profile['contribution_types']['docs'] > 1:
        archetype_indicators.append('doc_writer')
    
    # Mentor archetype
    if collaboration_profile['collaboration_style']['mentorship_score'] > 3:
        archetype_indicators.append('mentor')
    
    # Leader archetype
    if collaboration_profile['collaboration_style']['leadership_score'] > 5:
        archetype_indicators.append('leader')
    
    collaboration_profile['archetype_indicators'] = archetype_indicators
    
    print(f"   📊 Analyzed {collaboration_profile['total_prs_created']} PRs, {collaboration_profile['total_prs_reviewed']} reviews")
    print(f"   🎭 Detected archetypes: {', '.join(archetype_indicators) if archetype_indicators else 'General Developer'}")
    
    return collaboration_profile


def classify_pr_type(pr):
    """
    Classify a pull request based on title and file changes.
    
    Args:
        pr: GitHub PR object
        
    Returns:
        str: Type classification ('feature', 'fix', 'docs', 'test', 'other')
    """
    title = pr.title.lower()
    
    # Check title for common patterns
    if any(keyword in title for keyword in ['feat:', 'feature:', 'add', 'implement', 'new']):
        return 'feature'
    elif any(keyword in title for keyword in ['fix:', 'bug:', 'hotfix:', 'patch:', 'resolve']):
        return 'fix'
    elif any(keyword in title for keyword in ['docs:', 'doc:', 'readme', 'documentation']):
        return 'docs'
    elif any(keyword in title for keyword in ['test:', 'tests:', 'testing', 'spec:']):
        return 'test'
    
    # Analyze file changes if available
    try:
        files = list(pr.get_files())[:10]  # Limit to avoid rate limits
        
        doc_files = sum(1 for f in files if any(ext in f.filename.lower() 
                                              for ext in ['.md', '.rst', '.txt', 'readme', 'doc']))
        test_files = sum(1 for f in files if any(ext in f.filename.lower() 
                                                for ext in ['test', 'spec', '__test__']))
        
        if doc_files > len(files) * 0.5:
            return 'docs'
        elif test_files > len(files) * 0.3:
            return 'test'
            
    except Exception:
        pass  # File analysis failed, rely on title only
    
    return 'other'


def analyze_code_style_from_commits(user, gemini_client, num_commits=10):
    """
    Fetch diffs for a sample of recent commits and use Gemini to classify the coding style.
    
    Args:
        user: GitHub user object
        gemini_client: Configured Gemini client
        num_commits: Number of recent commits to analyze
        
    Returns:
        dict: Code style profile with classification and confidence
    """
    print(f"🔍 Analyzing code style from {num_commits} recent commits...")
    
    code_style_profile = {
        'style_classification': 'unknown',
        'confidence': 0.0,
        'analyzed_commits': 0,
        'sample_languages': [],
        'style_indicators': {}
    }
    
    try:
        # Get the user's most active repository
        repos = list(user.get_repos(type='all', sort='updated'))[:5]
        
        if not repos:
            print("   ⚠️ No repositories found for code analysis")
            return code_style_profile
        
        most_active_repo = repos[0]  # Most recently updated repo
        print(f"   📂 Analyzing commits from: {most_active_repo.name}")
        
        # Get recent commits
        commits = list(most_active_repo.get_commits())[:num_commits]
        
        code_samples = []
        analyzed_count = 0
        
        for commit in commits:
            try:
                # Get the commit details with file changes
                commit_details = most_active_repo.get_commit(commit.sha)
                
                for file in commit_details.files[:3]:  # Limit files per commit
                    # Skip non-code files
                    if not is_code_file(file.filename):
                        continue
                    
                    # Get the patch (diff) content
                    if file.patch and len(file.patch) < 2000:  # Limit patch size
                        code_samples.append({
                            'filename': file.filename,
                            'patch': file.patch,
                            'language': detect_language_from_filename(file.filename)
                        })
                        analyzed_count += 1
                        
                        if len(code_samples) >= 5:  # Limit total samples
                            break
                
                if len(code_samples) >= 5:
                    break
                    
            except Exception:
                continue  # Skip problematic commits
        
        code_style_profile['analyzed_commits'] = analyzed_count
        
        if not code_samples:
            print("   ⚠️ No code samples found for analysis")
            return code_style_profile
        
        # Prepare code samples for Gemini analysis
        combined_code = "\n\n--- CODE SAMPLE ---\n".join([
            f"File: {sample['filename']} ({sample['language']})\n{sample['patch']}" 
            for sample in code_samples[:3]  # Limit to 3 samples
        ])
        
        # Extract unique languages
        languages = list(set(sample['language'] for sample in code_samples if sample['language']))
        code_style_profile['sample_languages'] = languages
        
        # Analyze with Gemini
        style_classification = analyze_code_style_with_gemini(combined_code, gemini_client)
        
        code_style_profile.update(style_classification)
        
        print(f"   🎨 Code style classified as: {code_style_profile['style_classification']}")
        print(f"   🔍 Confidence: {code_style_profile['confidence']:.1%}")
        
    except Exception as e:
        print(f"   ⚠️ Code style analysis failed: {str(e)[:50]}...")
    
    return code_style_profile


def is_code_file(filename):
    """Check if a filename represents a code file."""
    code_extensions = [
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', 
        '.rs', '.swift', '.kt', '.scala', '.clj', '.r', '.m', '.sh', '.sql', '.html', '.css'
    ]
    return any(filename.lower().endswith(ext) for ext in code_extensions)


def detect_language_from_filename(filename):
    """Detect programming language from filename."""
    language_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java',
        '.cpp': 'C++', '.c': 'C', '.h': 'C/C++', '.cs': 'C#', '.php': 'PHP',
        '.rb': 'Ruby', '.go': 'Go', '.rs': 'Rust', '.swift': 'Swift', '.kt': 'Kotlin',
        '.scala': 'Scala', '.clj': 'Clojure', '.r': 'R', '.m': 'Objective-C',
        '.sh': 'Shell', '.sql': 'SQL', '.html': 'HTML', '.css': 'CSS'
    }
    
    for ext, lang in language_map.items():
        if filename.lower().endswith(ext):
            return lang
    return 'Unknown'


def analyze_code_style_with_gemini(code_samples, gemini_client):
    """
    Use Gemini to analyze code style and classify it.
    
    Args:
        code_samples: Combined code samples as string
        gemini_client: Configured Gemini client
        
    Returns:
        dict: Style classification results
    """
    prompt = f"""Analyze the following code samples and classify the coding style. Focus on:

1. **Elegance & Minimalism**: Clean, concise, readable code with minimal complexity
2. **Dense & Algorithmic**: Complex, highly optimized, or algorithmically intensive code
3. **Experimental & Cutting-Edge**: Uses new patterns, frameworks, or unconventional approaches
4. **Robust & Foundational**: Solid, well-structured, production-ready code with good practices

CODE SAMPLES:
{code_samples}

Please respond with ONLY a JSON object in this format:
{{
    "style_classification": "elegant_minimalist|dense_algorithmic|experimental_cutting_edge|robust_foundational",
    "confidence": 0.85,
    "reasoning": "Brief explanation of why this classification was chosen",
    "style_indicators": {{
        "elegance_score": 0.7,
        "complexity_score": 0.3,
        "experimental_score": 0.2,
        "robustness_score": 0.8
    }}
}}"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
        )
        
        if response and response.text:
            # Clean the response and parse JSON
            clean_response = response.text.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:-3]
            elif clean_response.startswith('```'):
                clean_response = clean_response[3:-3]
            
            result = json.loads(clean_response)
            
            # Validate and return
            if 'style_classification' in result and 'confidence' in result:
                return result
    
    except Exception as e:
        print(f"   ⚠️ Gemini code analysis failed: {str(e)[:50]}...")
    
    # Fallback result
    return {
        'style_classification': 'robust_foundational',
        'confidence': 0.5,
        'reasoning': 'Default classification due to analysis failure',
        'style_indicators': {
            'elegance_score': 0.5,
            'complexity_score': 0.5, 
            'experimental_score': 0.5,
            'robustness_score': 0.5
        }
    }


def analyze_user_profile(username, github_token, gemini_api_key, days_window=90):
    
    commit_times = []
    commit_days = []
    
    for repo in user.get_repos(sort="updated"):
        repo_updated = repo.updated_at.replace(tzinfo=None) if repo.updated_at.tzinfo else repo.updated_at
        if repo_updated < time_window_start:
            break
            
        try:
            commits = list(repo.get_commits(author=user, since=time_window_start))
            for commit in commits:
                commit_time = commit.commit.author.date
                if commit_time:
                    # Convert to naive datetime
                    if commit_time.tzinfo:
                        commit_time = commit_time.replace(tzinfo=None)
                    commit_times.append(commit_time.hour)
                    commit_days.append(commit_time.weekday())  # 0=Monday, 6=Sunday
        except:
            continue
    
    if not commit_times:
        return {
            "activity_level": "Unknown",
            "time_of_day": "Unknown",
            "day_pattern": "Unknown",
            "total_commits": 0
        }
    
    # Analyze time of day patterns
    hour_counts = Counter(commit_times)
    day_counts = Counter(commit_days)
    
    # Determine time of day preference
    morning_commits = sum(hour_counts.get(h, 0) for h in range(6, 12))
    afternoon_commits = sum(hour_counts.get(h, 0) for h in range(12, 18))
    evening_commits = sum(hour_counts.get(h, 0) for h in range(18, 24))
    night_commits = sum(hour_counts.get(h, 0) for h in range(0, 6))
    
    time_patterns = {
        "Morning Coder": morning_commits,
        "Day Coder": afternoon_commits,
        "Evening Coder": evening_commits,
        "Night Owl": night_commits
    }
    
    primary_time = max(time_patterns, key=time_patterns.get)
    
    # Determine activity level
    total_commits = len(commit_times)
    commits_per_day = total_commits / days_window
    
    if commits_per_day >= 2:
        activity_level = "Highly Active"
    elif commits_per_day >= 0.5:
        activity_level = "Consistent"
    elif commits_per_day >= 0.1:
        activity_level = "Casual"
    else:
        activity_level = "Sporadic"
    
    # Determine day pattern
    weekday_commits = sum(day_counts.get(d, 0) for d in range(5))  # Mon-Fri
    weekend_commits = sum(day_counts.get(d, 0) for d in [5, 6])   # Sat-Sun
    
    if weekend_commits > weekday_commits * 0.5:
        day_pattern = "Weekend Warrior"
    else:
        day_pattern = "Weekday Developer"
    
    return {
        "activity_level": activity_level,
        "time_of_day": primary_time,
        "day_pattern": day_pattern,
        "total_commits": total_commits,
        "commits_per_day": round(commits_per_day, 2),
        "time_distribution": {
            "morning": morning_commits,
            "afternoon": afternoon_commits,
            "evening": evening_commits,
            "night": night_commits
        }
    }

def analyze_user_profile(username, github_token, gemini_api_key, days_window=90):
    """
    Analyzes a GitHub user's profile and saves it to a JSON file.
    """
    # Initialize the Gemini client
    gemini_client = genai.Client(api_key=gemini_api_key)
    
    # Initialize the GitHub client
    g = Github(github_token)

    try:
        user = g.get_user(username)
    except GithubException:
        print(f"❌ ERROR: Could not find GitHub user '{username}'")
        return None

    # Easter Egg for Linus Torvalds
    if username.lower() == 'torvalds':
        print("Recognized a legend. Using pre-defined profile for Linus Torvalds.")
        profile = {
            "username": "torvalds",
            "is_legend": True,
            "analysis_type": "pre-defined",
            "language_profile": {"C": 100.0},
            "domain_focus": ["Operating Systems Kernel"],
            "contribution_style": "Benevolent Dictator for Life",
            "commit_cadence": {"activity_level": "God-Tier", "time_of_day": "All the time"},
        }
        
        # Generate special image prompts for Linus
        print(f"🎨 Generating legendary image prompts...")
        from .prompt_generator import generate_linus_prompt
        
        main_prompt = generate_linus_prompt()
        
        # Create simple variations for Linus
        prompt_variations = [
            {
                'variation': 1,
                'randomness_level': 0.0,
                'prompt': main_prompt.replace('Create a legendary portrait', 'Create a professional headshot style portrait').replace('Photorealistic portrait style', 'Corporate executive portrait style')
            },
            {
                'variation': 2,
                'randomness_level': 0.15,
                'prompt': main_prompt.replace('Create a legendary portrait', 'Create a detailed pencil sketch').replace('Photorealistic portrait style', 'Classical charcoal drawing style').replace('Professional lighting', 'Soft studio lighting')
            },
            {
                'variation': 3,
                'randomness_level': 0.3,
                'prompt': main_prompt.replace('Create a legendary portrait', 'Create a cyberpunk-inspired digital art').replace('Photorealistic portrait style', 'Futuristic cyberpunk art style').replace('Professional blues and greens', 'Neon blues and electric greens')
            }
        ]
        
        profile["image_prompts"] = {
            "main_prompt": main_prompt,
            "variations": prompt_variations
        }
    else:
        print(f"Analyzing profile for {username}...")
        print(f"📊 Fetching language distribution...")
        lang_dist = get_language_distribution(user, days_window)
        
        print(f"🧠 Analyzing domain focus with Gemini AI...")
        domain_focus, debug_info = get_area_of_focus(user, gemini_client, days_window)
        
        print(f"🎨 Analyzing contribution style...")
        contribution_style = get_contribution_style(user, days_window)
        
        print(f"⏰ Analyzing commit cadence...")
        commit_cadence = get_commit_cadence(user, [repo.name for repo in user.get_repos()[:10]], days_window)
        
        print(f"🔍 Analyzing code originality...")
        originality_analysis = analyze_code_originality(user, days_window)
        
        print(f"� Detecting high-profile contributions...")
        high_profile_contributions = detect_high_profile_contributions(user, days_window)
        
        print(f"💻 Classifying frontend/backend focus...")
        frontend_backend_focus = classify_frontend_backend_focus(user, gemini_client, days_window)
        
        print(f"🤝 Analyzing Pull Request patterns...")
        collaboration_profile = analyze_pull_requests(user, days_window)
        
        print(f"🎨 Analyzing code style from recent commits...")
        code_style_profile = analyze_code_style_from_commits(user, gemini_client, 10)
        
        print(f"�🎨 Generating image prompts...")
        # Import here to avoid circular imports
        from .prompt_generator import generate_image_prompt, create_prompt_variations
        
        # Create the complete profile first
        temp_profile = {
            "username": username,
            "last_updated": datetime.utcnow().isoformat(),
            "analysis_parameters": {"days_window": days_window},
            "language_profile": lang_dist,
            "domain_focus": domain_focus,
            "contribution_style": contribution_style,
            "commit_cadence": commit_cadence,
            "originality_analysis": originality_analysis,
            "high_profile_contributions": high_profile_contributions,
            "frontend_backend_focus": frontend_backend_focus,
            "collaboration_profile": collaboration_profile,
            "code_style_profile": code_style_profile,
        }
        
        # Generate prompts based on the profile
        main_prompt = generate_image_prompt(temp_profile)
        prompt_variations = create_prompt_variations(temp_profile)

        profile = {
            "username": username,
            "last_updated": datetime.utcnow().isoformat(),
            "analysis_parameters": {"days_window": days_window},
            "language_profile": lang_dist,
            "domain_focus": domain_focus,
            "contribution_style": contribution_style,
            "commit_cadence": commit_cadence,
            "originality_analysis": originality_analysis,
            "high_profile_contributions": high_profile_contributions,
            "frontend_backend_focus": frontend_backend_focus,
            "collaboration_profile": collaboration_profile,
            "code_style_profile": code_style_profile,
            "image_prompts": {
                "main_prompt": main_prompt,
                "variations": prompt_variations
            },
            "debug_info": debug_info
        }

    output_dir = 'user_profile'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_path = os.path.join(output_dir, f'{username}_profile.json')
    with open(file_path, 'w') as f:
        json.dump(profile, f, indent=4)
        
    print(f"✅ User profile saved to {file_path}")
    return profile


# =============================================================================
# PHASE 5: GitHub Profile Picture Integration
# =============================================================================

def get_github_profile_picture(username, output_dir='profile_pictures'):
    """
    Fetch the user's GitHub profile picture URL and download the image.
    
    Args:
        username: GitHub username
        output_dir: Directory to save the profile picture
        
    Returns:
        dict: Result with success status and image path or error message
    """
    import requests
    import mimetypes
    
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Get GitHub token
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            return {
                'success': False,
                'error': 'GITHUB_TOKEN not found in environment variables'
            }
        
        # Initialize GitHub client
        github_client = Github(github_token)
        
        # Get user profile
        user = github_client.get_user(username)
        avatar_url = user.avatar_url
        
        if not avatar_url:
            return {
                'success': False,
                'error': f'No profile picture found for user {username}'
            }
        
        # Download the profile picture
        print(f"📸 Downloading profile picture for {username}...")
        response = requests.get(avatar_url)
        response.raise_for_status()
        
        # Determine file extension from content type
        content_type = response.headers.get('content-type', 'image/jpeg')
        extension = mimetypes.guess_extension(content_type) or '.jpg'
        
        # Save the image
        image_filename = f"{username}_profile{extension}"
        image_path = os.path.join(output_dir, image_filename)
        
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Profile picture saved to {image_path}")
        
        return {
            'success': True,
            'image_path': image_path,
            'avatar_url': avatar_url,
            'content_type': content_type
        }
        
    except GithubException as e:
        return {
            'success': False,
            'error': f'GitHub API error: {str(e)}'
        }
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Download error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def validate_profile_image(image_path):
    """
    Validate image format and quality for generation input.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        dict: Validation result with success status and details
    """
    import mimetypes
    from PIL import Image
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': f'Image file not found: {image_path}'
            }
        
        # Check file size (max 10MB)
        file_size = os.path.getsize(image_path)
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_size:
            return {
                'success': False,
                'error': f'Image file too large: {file_size} bytes (max: {max_size} bytes)'
            }
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(image_path)
        supported_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        
        if mime_type not in supported_types:
            return {
                'success': False,
                'error': f'Unsupported image format: {mime_type}. Supported: {supported_types}'
            }
        
        # Validate image with PIL
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Check minimum dimensions
            min_dimension = 64
            if width < min_dimension or height < min_dimension:
                return {
                    'success': False,
                    'error': f'Image too small: {width}x{height} (minimum: {min_dimension}x{min_dimension})'
                }
            
            # Check if image is reasonable size (not too large)
            max_dimension = 2048
            if width > max_dimension or height > max_dimension:
                return {
                    'success': False,
                    'error': f'Image too large: {width}x{height} (maximum: {max_dimension}x{max_dimension})'
                }
        
        return {
            'success': True,
            'file_size': file_size,
            'mime_type': mime_type,
            'dimensions': (width, height),
            'format': img.format
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Image validation error: {str(e)}'
        }


def prepare_image_for_generation(image_path):
    """
    Prepare the profile picture for Gemini image generation.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        dict: Prepared image data and metadata
    """
    import base64
    import mimetypes
    
    try:
        # Validate the image first
        validation_result = validate_profile_image(image_path)
        if not validation_result['success']:
            return validation_result
        
        # Read image as binary data
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(image_path)
        
        # Encode as base64 for display/debugging purposes
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        return {
            'success': True,
            'image_data': image_data,
            'mime_type': mime_type,
            'base64_data': base64_data,
            'file_size': len(image_data),
            'validation_info': validation_result
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Image preparation error: {str(e)}'
        }
