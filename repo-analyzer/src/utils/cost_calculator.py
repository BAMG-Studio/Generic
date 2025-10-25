"""
Advanced Cost Calculation with SCC and Git Prime Integration
Provides comprehensive cost analysis using multiple methodologies
"""
import subprocess
import json
import re
from typing import Dict, Any, Optional, List
from pathlib import Path


class CostCalculator:
    """
    Advanced cost calculator with multiple analysis methods:
    - COCOMO II (Constructive Cost Model)
    - SCC (Sloc Cloc and Code) for accurate code metrics
    - Git Prime for development velocity analysis
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize cost calculator
        
        Args:
            config: Configuration dictionary with cost parameters
        """
        self.config = config or {}
        self.hourly_rate = self.config.get('hourly_rate', 100.0)
        self.cocomo_params = self.config.get('cocomo_params', {
            'a': 2.94,  # COCOMO II organic mode
            'b': 1.14,
            'monthly_hours': 152  # Standard working hours per month
        })
    
    def run_scc(self, repo_path: str) -> Dict[str, Any]:
        """
        Run SCC (Sloc Cloc and Code) on repository
        
        SCC provides accurate code metrics including:
        - Lines of code by language
        - Complexity metrics
        - Estimated development effort
        - Estimated cost
        
        Args:
            repo_path: Path to repository
            
        Returns:
            SCC analysis results
        """
        try:
            # Check if scc is installed
            result = subprocess.run(
                ['which', 'scc'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️  SCC not installed. Installing...")
                return self._install_and_run_scc(repo_path)
            
            # Run SCC with JSON output
            result = subprocess.run(
                ['scc', '--format', 'json', '--no-cocomo', repo_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                scc_data = json.loads(result.stdout)
                return self._parse_scc_output(scc_data)
            else:
                print(f"⚠️  SCC failed: {result.stderr}")
                return self._get_empty_scc_result()
                
        except subprocess.TimeoutExpired:
            print("⚠️  SCC timed out after 5 minutes")
            return self._get_empty_scc_result()
        except Exception as e:
            print(f"⚠️  SCC error: {e}")
            return self._get_empty_scc_result()
    
    def _install_and_run_scc(self, repo_path: str) -> Dict[str, Any]:
        """Provide instructions for installing SCC"""
        print("📥 SCC (Sloc Cloc and Code) is not installed.")
        print("   Please install SCC for accurate code metrics:")
        print("   ")
        print("   Option 1 - Download Binary (Recommended):")
        print("   wget https://github.com/boyter/scc/releases/download/v3.1.0/scc_3.1.0_Linux_x86_64.tar.gz")
        print("   tar -xzf scc_3.1.0_Linux_x86_64.tar.gz")
        print("   sudo mv scc /usr/local/bin/")
        print("   ")
        print("   Option 2 - Using Snap:")
        print("   sudo snap install scc")
        print("   ")
        print("   See INSTALL_SCC.md for more options")
        print("   ")
        print("   Continuing with basic estimation...")
        return self._get_empty_scc_result()
    
    def _parse_scc_output(self, scc_data: List[Dict]) -> Dict[str, Any]:
        """Parse SCC JSON output"""
        total_lines = 0
        total_code = 0
        total_comments = 0
        total_blanks = 0
        total_complexity = 0
        total_bytes = 0
        languages = {}
        
        for lang_data in scc_data:
            lang_name = lang_data.get('Name', 'Unknown')
            lines = lang_data.get('Lines', 0)
            code = lang_data.get('Code', 0)
            comments = lang_data.get('Comment', 0)
            blanks = lang_data.get('Blank', 0)
            complexity = lang_data.get('Complexity', 0)
            bytes_count = lang_data.get('Bytes', 0)
            files = lang_data.get('Count', 0)
            
            total_lines += lines
            total_code += code
            total_comments += comments
            total_blanks += blanks
            total_complexity += complexity
            total_bytes += bytes_count
            
            languages[lang_name] = {
                'files': files,
                'lines': lines,
                'code': code,
                'comments': comments,
                'blanks': blanks,
                'complexity': complexity,
                'bytes': bytes_count
            }
        
        return {
            'total_lines': total_lines,
            'total_code': total_code,
            'total_comments': total_comments,
            'total_blanks': total_blanks,
            'total_complexity': total_complexity,
            'total_bytes': total_bytes,
            'languages': languages,
            'kloc': total_code / 1000.0  # Thousands of lines of code
        }
    
    def _get_empty_scc_result(self) -> Dict[str, Any]:
        """Return empty SCC result structure"""
        return {
            'total_lines': 0,
            'total_code': 0,
            'total_comments': 0,
            'total_blanks': 0,
            'total_complexity': 0,
            'total_bytes': 0,
            'languages': {},
            'kloc': 0
        }
    
    def run_git_prime(self, repo_path: str) -> Dict[str, Any]:
        """
        Run git-quick-stats (git-prime alternative) for development velocity
        
        Analyzes:
        - Author contribution patterns
        - Commit velocity
        - Code churn
        - Development trends
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Git prime analysis results
        """
        try:
            git_stats = {
                'commits_by_author': {},
                'lines_by_author': {},
                'commits_per_day': {},
                'total_additions': 0,
                'total_deletions': 0,
                'total_churn': 0
            }
            
            # Get commits by author
            result = subprocess.run(
                ['git', '-C', repo_path, 'shortlog', '-sn', '--all'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        match = re.match(r'\s*(\d+)\s+(.+)', line)
                        if match:
                            count = int(match.group(1))
                            author = match.group(2)
                            git_stats['commits_by_author'][author] = count
            
            # Get line changes by author
            result = subprocess.run(
                ['git', '-C', repo_path, 'log', '--all', '--numstat', '--pretty=format:%ae'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                current_author = None
                for line in result.stdout.split('\n'):
                    if '@' in line:
                        current_author = line.strip()
                        if current_author not in git_stats['lines_by_author']:
                            git_stats['lines_by_author'][current_author] = {
                                'additions': 0,
                                'deletions': 0
                            }
                    elif line.strip() and current_author:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            try:
                                additions = int(parts[0]) if parts[0] != '-' else 0
                                deletions = int(parts[1]) if parts[1] != '-' else 0
                                git_stats['lines_by_author'][current_author]['additions'] += additions
                                git_stats['lines_by_author'][current_author]['deletions'] += deletions
                                git_stats['total_additions'] += additions
                                git_stats['total_deletions'] += deletions
                            except ValueError:
                                pass
            
            git_stats['total_churn'] = git_stats['total_additions'] + git_stats['total_deletions']
            
            return git_stats
            
        except Exception as e:
            print(f"⚠️  Git prime analysis error: {e}")
            return {
                'commits_by_author': {},
                'lines_by_author': {},
                'commits_per_day': {},
                'total_additions': 0,
                'total_deletions': 0,
                'total_churn': 0
            }
    
    def calculate_cocomo_cost(
        self,
        kloc: float,
        commits: int = 0,
        contributors: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate development cost using COCOMO II model
        
        Args:
            kloc: Thousands of lines of code
            commits: Total number of commits
            contributors: Total number of contributors
            
        Returns:
            Cost analysis dictionary
        """
        # COCOMO II: Effort = a * (KLOC^b)
        a = self.cocomo_params['a']
        b = self.cocomo_params['b']
        monthly_hours = self.cocomo_params['monthly_hours']
        
        if kloc > 0:
            effort_months = a * (kloc ** b)
        else:
            # Fallback: estimate from commits
            effort_months = (commits * 3) / monthly_hours if commits > 0 else 0
        
        effort_hours = effort_months * monthly_hours
        estimated_cost = effort_hours * self.hourly_rate
        
        # Calculate development time
        if contributors > 0:
            dev_time_months = effort_months / contributors
        else:
            dev_time_months = effort_months
        
        return {
            'kloc': round(kloc, 2),
            'effort_months': round(effort_months, 2),
            'effort_hours': round(effort_hours, 2),
            'estimated_cost': round(estimated_cost, 2),
            'hourly_rate': self.hourly_rate,
            'development_time_months': round(dev_time_months, 2),
            'cocomo_parameters': self.cocomo_params
        }
    
    def calculate_comprehensive_cost(
        self,
        repo_path: str,
        commits: int = 0,
        contributors: int = 0,
        dependencies: int = 0
    ) -> Dict[str, Any]:
        """
        Comprehensive cost analysis combining SCC, Git Prime, and COCOMO II
        
        Args:
            repo_path: Path to repository
            commits: Total commits
            contributors: Total contributors
            dependencies: Total dependencies
            
        Returns:
            Comprehensive cost analysis
        """
        # Run SCC analysis
        scc_results = self.run_scc(repo_path)
        
        # Run Git Prime analysis
        git_prime_results = self.run_git_prime(repo_path)
        
        # Calculate COCOMO cost
        cocomo_results = self.calculate_cocomo_cost(
            scc_results['kloc'],
            commits,
            contributors
        )
        
        # Combine all metrics
        comprehensive_analysis = {
            'cocomo': cocomo_results,
            'scc': scc_results,
            'git_prime': git_prime_results,
            'metrics': {
                'total_commits': commits,
                'total_contributors': contributors,
                'total_dependencies': dependencies,
                'commits_per_contributor': round(commits / contributors, 2) if contributors > 0 else 0,
                'commits_per_dependency': round(commits / dependencies, 2) if dependencies > 0 else 0,
                'cost_per_dependency': round(cocomo_results['estimated_cost'] / dependencies, 2) if dependencies > 0 else 0,
                'cost_per_commit': round(cocomo_results['estimated_cost'] / commits, 2) if commits > 0 else 0,
                'lines_per_dependency': round(scc_results['total_code'] / dependencies, 2) if dependencies > 0 else 0,
                'complexity_per_kloc': round(scc_results['total_complexity'] / scc_results['kloc'], 2) if scc_results['kloc'] > 0 else 0
            },
            'summary': {
                'estimated_cost': cocomo_results['estimated_cost'],
                'estimated_hours': cocomo_results['effort_hours'],
                'total_lines': scc_results['total_lines'],
                'total_code': scc_results['total_code'],
                'total_complexity': scc_results['total_complexity'],
                'code_churn': git_prime_results['total_churn'],
                'dependencies_commits_ratio': f"{dependencies}:{commits}"
            }
        }
        
        return comprehensive_analysis
