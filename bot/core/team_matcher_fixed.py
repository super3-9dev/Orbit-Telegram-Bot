#!/usr/bin/env python3
"""
Team matching module for arbitrage detection.
Replaces OpenAI with Python-based fuzzy string matching.
"""

import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class TeamMatcher:
    """
    Handles team name matching between Orbit and Golbet data.
    Uses fuzzy string matching and normalization for accurate results.
    """
    
    def __init__(self, match_threshold: int = 80):
        self.match_threshold = match_threshold
        self.team_cache = {}  # Cache for team name mappings
        
        # Common team name variations and replacements
        self.team_replacements = {
            'united': 'utd',
            'united states': 'usa',
            'fc': '',
            'football club': '',
            'real madrid': 'madrid',
            'bayern munich': 'bayern',
            'manchester united': 'man utd',
            'manchester city': 'man city',
            'arsenal fc': 'arsenal',
            'chelsea fc': 'chelsea',
            'liverpool fc': 'liverpool',
            'tottenham hotspur': 'tottenham',
            'ac milan': 'milan',
            'inter milan': 'inter',
            'juventus fc': 'juventus',
            'barcelona fc': 'barcelona',
            'atletico madrid': 'atletico',
            'psg': 'paris saint-germain',
            'paris saint germain': 'paris saint-germain',
            'borussia dortmund': 'dortmund',
            'ajax amsterdam': 'ajax',
            'benfica': 'sl benfica',
            'porto': 'fc porto',
            'celtic fc': 'celtic',
            'rangers fc': 'rangers',
            'galatasaray': 'galatasaray sk',
            'fenerbahce': 'fenerbahce sk',
            'besiktas': 'besiktas jk',
            'shakhtar donetsk': 'shakhtar',
            'dinamo kiev': 'dinamo kyiv',
            'red star belgrade': 'crvena zvezda',
            'partizan belgrade': 'partizan',
            'olympiacos': 'olympiacos fc',
            'panathinaikos': 'panathinaikos fc',
            'ae athens': 'ae athens fc',
            'paok thessaloniki': 'paok',
            'slavia prague': 'slavia',
            'sparta prague': 'sparta',
            'legia warsaw': 'legia',
            'lechia gdansk': 'lechia',
            'dinamo zagreb': 'dinamo',
            'hajduk split': 'hajduk',
            'red bull salzburg': 'salzburg',
            'rapid vienna': 'rapid wien',
            'austria vienna': 'austria wien',
            'young boys': 'young boys bern',
            'basel': 'fc basel',
            'grasshoppers': 'grasshopper club',
            'servette': 'servette fc',
            'luzern': 'fc luzern',
            'st gallen': 'fc st gallen',
            'zurich': 'fc zurich',
            'thun': 'fc thun',
            'sion': 'fc sion',
            'bellinzona': 'ac bellinzona',
            'neuchatel xamax': 'neuchatel',
            'lausanne': 'fc lausanne',
            'yverdon': 'yverdon sport',
            'kriens': 'sc kriens',
            'wil': 'fc wil 1900',
            'schaffhausen': 'fc schaffhausen',
            'aarau': 'fc aarau',
            'winterthur': 'fc winterthur',
            'cham': 'sc cham',
            'zug': 'fc zug 94'
        }
    
    def normalize_team_name(self, team_name: str) -> str:
        """
        Normalize team names for better matching.
        
        Args:
            team_name: Raw team name
            
        Returns:
            Normalized team name
        """
        if not team_name:
            return ""
        
        # Convert to lowercase and remove extra spaces
        normalized = team_name.lower().strip()
        
        # Apply replacements
        for old, new in self.team_replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove special characters and extra spaces
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def calculate_similarity(self, team1: str, team2: str) -> float:
        """
        Calculate similarity between two team names.
        
        Args:
            team1: First team name
            team2: Second team name
            
        Returns:
            Similarity percentage (0-100)
        """
        if not team1 or not team2:
            return 0.0
        
        # Normalize both names
        norm1 = self.normalize_team_name(team1)
        norm2 = self.normalize_team_name(team2)
        
        if norm1 == norm2:
            return 100.0
        
        # Simple word-based similarity
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        similarity = (len(intersection) / len(union)) * 100
        return similarity
    
    def find_best_match(self, target_team: str, candidate_teams: List[str]) -> Tuple[str, float]:
        """
        Find the best matching team from a list of candidates.
        
        Args:
            target_team: Team to match
            candidate_teams: List of candidate teams
            
        Returns:
            Tuple of (best_match, similarity_score)
        """
        if not candidate_teams:
            return "", 0.0
        
        best_match = ""
        best_similarity = 0.0
        
        for candidate in candidate_teams:
            similarity = self.calculate_similarity(target_team, candidate)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = candidate
        
        return best_match, best_similarity
    
    def match_all_teams(self, orbit_teams: List[str], golbet_teams: List[str]) -> Dict[str, str]:
        """
        Match teams between Orbit and Golbet data.
        
        Args:
            orbit_teams: List of team names from Orbit
            golbet_teams: List of team names from Golbet
            
        Returns:
            Dictionary mapping Orbit teams to Golbet teams
        """
        matches = {}
        
        for orbit_team in orbit_teams:
            if not orbit_team:
                continue
            
            best_match, similarity = self.find_best_match(orbit_team, golbet_teams)
            
            if similarity >= self.match_threshold:
                matches[orbit_team] = best_match
                print(f"[TEAM MATCHER] ✅ {orbit_team} ↔ {best_match} ({similarity:.1f}%)")
            else:
                print(f"[TEAM MATCHER] ❌ {orbit_team} - No good match found (best: {similarity:.1f}%)")
        
        return matches


class ArbitrageCalculator:
    """
    Calculates arbitrage opportunities and validates thresholds.
    """
    
    def __init__(self, min_threshold: float = -1.0, max_threshold: float = 30.0):
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
    
    def calculate_odds_difference(self, orbit_lay: float, golbet_back: float) -> Tuple[float, float]:
        """
        Calculate the difference between Orbit lay odds and Golbet back odds.
        
        Args:
            orbit_lay: LAY odds from Orbit
            golbet_back: BACK odds from Golbet
            
        Returns:
            Tuple of (numeric_difference, percentage_difference)
        """
        if orbit_lay <= 0 or golbet_back <= 0:
            return 0.0, 0.0
        
        numeric_diff = golbet_back - orbit_lay
        percentage_diff = (numeric_diff / orbit_lay) * 100
        
        return numeric_diff, percentage_diff
    
    def is_valid_opportunity(self, orbit_lay: float, golbet_back: float) -> bool:
        """
        Check if the odds difference is within the valid threshold range.
        
        Args:
            orbit_lay: LAY odds from Orbit
            golbet_back: BACK odds from Golbet
            
        Returns:
            True if within threshold, False otherwise
        """
        _, percentage_diff = self.calculate_odds_difference(orbit_lay, golbet_back)
        return self.min_threshold <= percentage_diff <= self.max_threshold
    
    def format_odds_difference(self, orbit_lay: float, golbet_back: float) -> str:
        """
        Format the odds difference for display.
        
        Args:
            orbit_lay: LAY odds from Orbit
            golbet_back: BACK odds from Golbet
            
        Returns:
            Formatted difference string
        """
        numeric_diff, percentage_diff = self.calculate_odds_difference(orbit_lay, golbet_back)
        
        if percentage_diff >= 0:
            return f"+{numeric_diff:.4f} (+{percentage_diff:.2f}%)"
        else:
            return f"{numeric_diff:.4f} ({percentage_diff:.2f}%)"


def find_arbitrage_opportunities(orbit_data: List[Dict], golbet_data: List[Dict]) -> List[Dict]:
    """
    Find arbitrage opportunities between Orbit and Golbet data.
    
    Args:
        orbit_data: List of Orbit market snapshots (format: [{"home": "Team A", "away": "Team B", "label": "1", "odds": 2.0}, ...])
        golbet_data: List of Golbet market snapshots (format: [{"home": "Team A", "away": "Team B", "label": "1", "odds": 2.0}, ...])
        
    Returns:
        List of arbitrage opportunities
    """
    try:
        print("[ARBITRAGE] Starting opportunity detection...")
        
        # Initialize components
        team_matcher = TeamMatcher(match_threshold=75)
        calculator = ArbitrageCalculator(min_threshold=-1.0, max_threshold=30.0)
        
        # Process Orbit data to extract team names and odds
        orbit_processed = []
        for match_data in orbit_data:
            if isinstance(match_data, list) and len(match_data) >= 4:
                # Extract team names from first item
                team_info = match_data[0]
                if isinstance(team_info, dict) and 'home' in team_info and 'away' in team_info:
                    home_team = team_info['home']
                    away_team = team_info['away']
                    team_name = f"{home_team} vs {away_team}"
                    
                    # Extract lay odds (assuming first odds is lay odds)
                    for item in match_data[1:]:
                        if isinstance(item, dict) and 'label' in item and 'odds' in item:
                            if item['label'] == '1':  # Home win
                                try:
                                    odds = float(item['odds'])
                                    orbit_processed.append({
                                        'team_name': team_name,
                                        'lay_odds': odds,
                                        'home_team': home_team,
                                        'away_team': away_team
                                    })
                                    break
                                except (ValueError, TypeError):
                                    continue
        
        # Process Golbet data to extract team names and odds
        golbet_processed = []
        for match_data in golbet_data:
            if isinstance(match_data, list) and len(match_data) >= 4:
                # Extract team names from first item
                team_info = match_data[0]
                if isinstance(team_info, dict) and 'home' in team_info and 'away' in team_info:
                    home_team = team_info['home']
                    away_team = team_info['away']
                    team_name = f"{home_team} vs {away_team}"
                    
                    # Extract back odds (assuming first odds is back odds)
                    for item in match_data[1:]:
                        if isinstance(item, dict) and 'label' in item and 'odds' in item:
                            if item['label'] == '1':  # Home win
                                try:
                                    odds = float(item['odds'])
                                    golbet_processed.append({
                                        'team_name': team_name,
                                        'back_odds': odds,
                                        'home_team': home_team,
                                        'away_team': away_team
                                    })
                                    break
                                except (ValueError, TypeError):
                                    continue
        
        print(f"[ARBITRAGE] Processed {len(orbit_processed)} Orbit matches and {len(golbet_processed)} Golbet matches")
        
        # Extract team names for matching
        orbit_teams = [item['team_name'] for item in orbit_processed]
        golbet_teams = [item['team_name'] for item in golbet_processed]
        
        print(f"[ARBITRAGE] Found {len(orbit_teams)} Orbit teams and {len(golbet_teams)} Golbet teams")
        
        # Match teams
        team_matches = team_matcher.match_all_teams(orbit_teams, golbet_teams)
        
        if not team_matches:
            print("[ARBITRAGE] No team matches found")
            return []
        
        print(f"[ARBITRAGE] Successfully matched {len(team_matches)} teams")
        
        # Find opportunities
        opportunities = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for orbit_team, golbet_team in team_matches.items():
            # Find corresponding data
            orbit_item = next((item for item in orbit_processed if item['team_name'] == orbit_team), None)
            golbet_item = next((item for item in golbet_processed if item['team_name'] == orbit_team), None)
            
            if not orbit_item or not golbet_item:
                continue
            
            # Extract odds
            orbit_lay = orbit_item.get('lay_odds', 0)
            golbet_back = golbet_item.get('back_odds', 0)
            
            if orbit_lay <= 0 or golbet_back <= 0:
                continue
            
            # Check if valid opportunity
            if calculator.is_valid_opportunity(orbit_lay, golbet_back):
                # Format odds difference
                odds_diff_str = calculator.format_odds_difference(orbit_lay, golbet_back)
                
                opportunity = {
                    "match_name": orbit_team,
                    "orbit_lay_odds": orbit_lay,
                    "comparison_odds": golbet_back,
                    "odds_difference": odds_diff_str,
                    "market_type": "1X2",
                    "detection_time": now_str
                }
                
                opportunities.append(opportunity)
                print(f"[ARBITRAGE] ✅ Opportunity found: {opportunity['match_name']} - {odds_diff_str}")
        
        print(f"[ARBITRAGE] Found {len(opportunities)} valid opportunities")
        return opportunities
        
    except Exception as e:
        print(f"[ARBITRAGE] Error finding opportunities: {e}")
        import traceback
        traceback.print_exc()
        return []
