#!/usr/bin/env python3
"""
Technical Document Review Module
Comprehensive analysis of document content from technical writing perspective
Includes tense analysis, coherence checking, and interactive comment processing
"""

import re
import json
import requests  # pip install requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Optional dependencies with graceful degradation
try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    HAS_TKINTER = True
except ImportError:
    print("⚠ tkinter not available - UI features disabled")
    HAS_TKINTER = False
    tk = None
    messagebox = None
    simpledialog = None

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade  # pip install textstat
    HAS_TEXTSTAT = True
except ImportError:
    print("⚠ textstat not available - readability metrics disabled")
    HAS_TEXTSTAT = False
    flesch_reading_ease = None
    flesch_kincaid_grade = None

try:
    import nltk  # pip install nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.tag import pos_tag
    from nltk.corpus import stopwords
    HAS_NLTK = True

    # Download required NLTK data (run once)
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('averaged_perceptron_tagger')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass
except ImportError:
    print("⚠ nltk not available - linguistic analysis disabled")
    HAS_NLTK = False
    nltk = None
    sent_tokenize = None
    word_tokenize = None
    pos_tag = None
    stopwords = None

@dataclass
class TenseAnalysis:
    """Analysis of verb tenses in text"""
    past_count: int = 0
    present_count: int = 0
    future_count: int = 0
    inconsistent_sentences: List[str] = None
    dominant_tense: str = ""
    consistency_score: float = 0.0
    
    def __post_init__(self):
        if self.inconsistent_sentences is None:
            self.inconsistent_sentences = []

@dataclass
class ReadabilityMetrics:
    """Readability and complexity metrics"""
    flesch_score: float = 0.0
    grade_level: float = 0.0
    avg_sentence_length: float = 0.0
    complex_word_ratio: float = 0.0
    passive_voice_ratio: float = 0.0

@dataclass
class CoherenceAnalysis:
    """Document coherence and flow analysis"""
    transition_score: float = 0.0
    topic_consistency: float = 0.0
    logical_flow: float = 0.0
    section_connectivity: float = 0.0

@dataclass
class CommentReview:
    """Interactive comment review with LLM"""
    original_comment: str
    llm_analysis: str
    suggested_action: str  # "accept", "revise", "clarify", "remove"
    revised_content: str = ""
    confidence_score: float = 0.0
    user_decision: str = ""  # User's final decision

class TechnicalDocumentReviewer:
    """Comprehensive technical document review system"""
    
    def __init__(self, openwebui_config: Dict):
        self.config = openwebui_config
        self.tense_patterns = {
            'past': [
                r'\b\w+ed\b',  # Regular past tense
                r'\bwas\b', r'\bwere\b', r'\bhad\b', r'\bdid\b',
                r'\bcompleted\b', r'\bfinished\b', r'\bimplemented\b'
            ],
            'present': [
                r'\bis\b', r'\bare\b', r'\bam\b', r'\bhave\b', r'\bhas\b',
                r'\bdo\b', r'\bdoes\b', r'\bworks\b', r'\bcontains\b'
            ],
            'future': [
                r'\bwill\b', r'\bshall\b', r'\bgoing to\b',
                r'\bplanned\b', r'\bscheduled\b', r'\bintended\b'
            ]
        }
        
        # Technical writing transition words for coherence analysis
        self.transition_indicators = [
            'however', 'therefore', 'furthermore', 'moreover', 'consequently',
            'additionally', 'similarly', 'likewise', 'conversely', 'nonetheless',
            'meanwhile', 'subsequently', 'finally', 'initially', 'first',
            'second', 'third', 'next', 'then', 'afterwards', 'previously'
        ]
        
        # Technical writing quality prompts
        self.review_prompts = {
            'cohesion': """
            Analyze this text section for cohesion and flow. Rate from 1-10 and provide specific feedback on:
            1. Logical sequence of ideas
            2. Effective transitions between concepts
            3. Clear topic progression
            4. Paragraph unity and coherence
            
            Provide a JSON response with:
            {
                "score": <1-10>,
                "feedback": ["specific issue 1", "specific issue 2"],
                "suggestions": ["improvement 1", "improvement 2"]
            }
            """,
            
            'clarity': """
            Evaluate this text for clarity and readability. Rate from 1-10 and analyze:
            1. Sentence structure and complexity
            2. Technical jargon usage and explanation
            3. Ambiguous or unclear statements
            4. Active vs passive voice usage
            
            Provide a JSON response with:
            {
                "score": <1-10>,
                "feedback": ["clarity issue 1", "clarity issue 2"],
                "suggestions": ["improvement 1", "improvement 2"],
                "jargon_issues": ["unexplained term 1", "unexplained term 2"]
            }
            """,
            
            'technical_accuracy': """
            Review this technical content for accuracy and completeness. Rate from 1-10:
            1. Technical correctness of statements
            2. Appropriate level of detail
            3. Missing critical information
            4. Outdated or incorrect information
            
            Provide a JSON response with:
            {
                "score": <1-10>,
                "feedback": ["accuracy concern 1", "accuracy concern 2"],
                "missing_info": ["missing detail 1", "missing detail 2"],
                "verification_needed": ["claim to verify 1", "claim to verify 2"]
            }
            """,
            
            'tense_consistency': """
            Analyze this text for tense consistency issues. Provide:
            1. Dominant tense that should be used
            2. Specific sentences with tense problems
            3. Corrections for inconsistent sentences
            
            Provide a JSON response with:
            {
                "dominant_tense": "<past/present/future>",
                "inconsistent_sentences": [{"original": "sentence", "corrected": "corrected version"}],
                "overall_consistency": <1-10>
            }
            """
        }
    
    def analyze_tense_consistency(self, text: str) -> TenseAnalysis:
        """Analyze tense consistency in text"""
        sentences = sent_tokenize(text)
        tense_analysis = TenseAnalysis()
        
        for sentence in sentences:
            sentence_tenses = {'past': 0, 'present': 0, 'future': 0}
            
            # Count tense indicators in each sentence
            for tense, patterns in self.tense_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, sentence, re.IGNORECASE)
                    sentence_tenses[tense] += len(matches)
            
            # Determine dominant tense for this sentence
            if any(sentence_tenses.values()):
                dominant = max(sentence_tenses, key=sentence_tenses.get)
                if dominant == 'past':
                    tense_analysis.past_count += 1
                elif dominant == 'present':
                    tense_analysis.present_count += 1
                elif dominant == 'future':
                    tense_analysis.future_count += 1
                
                # Check for mixed tenses in single sentence
                tense_count = sum(1 for count in sentence_tenses.values() if count > 0)
                if tense_count > 1:
                    tense_analysis.inconsistent_sentences.append(sentence)
        
        # Determine overall dominant tense
        total_counts = {
            'past': tense_analysis.past_count,
            'present': tense_analysis.present_count,
            'future': tense_analysis.future_count
        }
        
        if any(total_counts.values()):
            tense_analysis.dominant_tense = max(total_counts, key=total_counts.get)
            
            # Calculate consistency score
            total_sentences = sum(total_counts.values())
            if total_sentences > 0:
                dominant_ratio = total_counts[tense_analysis.dominant_tense] / total_sentences
                inconsistency_penalty = len(tense_analysis.inconsistent_sentences) / len(sentences)
                tense_analysis.consistency_score = max(0, (dominant_ratio - inconsistency_penalty) * 10)
        
        return tense_analysis
    
    def calculate_readability_metrics(self, text: str) -> ReadabilityMetrics:
        """Calculate readability and complexity metrics"""
        metrics = ReadabilityMetrics()
        
        if not text.strip():
            return metrics
        
        try:
            # Basic readability scores
            metrics.flesch_score = flesch_reading_ease(text)
            metrics.grade_level = flesch_kincaid_grade(text)
            
            # Sentence length analysis
            sentences = sent_tokenize(text)
            if sentences:
                total_words = sum(len(word_tokenize(sentence)) for sentence in sentences)
                metrics.avg_sentence_length = total_words / len(sentences)
            
            # Complex word ratio (3+ syllables)
            words = word_tokenize(text.lower())
            complex_words = [word for word in words if self._count_syllables(word) >= 3]
            if words:
                metrics.complex_word_ratio = len(complex_words) / len(words)
            
            # Passive voice detection
            passive_count = len(re.findall(r'\b(?:was|were|been|being)\s+\w+ed\b', text, re.IGNORECASE))
            if sentences:
                metrics.passive_voice_ratio = passive_count / len(sentences)
                
        except Exception as e:
            print(f"Error calculating readability metrics: {e}")
        
        return metrics
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def analyze_coherence(self, text: str, section_context: str = "") -> CoherenceAnalysis:
        """Analyze document coherence and flow"""
        analysis = CoherenceAnalysis()
        
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            return analysis
        
        # Transition word analysis
        transition_count = 0
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for transition in self.transition_indicators:
                if transition in sentence_lower:
                    transition_count += 1
                    break
        
        analysis.transition_score = min(10, (transition_count / len(sentences)) * 20)
        
        # Topic consistency (basic keyword overlap between sentences)
        keywords_per_sentence = []
        stop_words = set(stopwords.words('english'))
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            keywords = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 3]
            keywords_per_sentence.append(set(keywords))
        
        # Calculate average keyword overlap between adjacent sentences
        if len(keywords_per_sentence) > 1:
            overlaps = []
            for i in range(len(keywords_per_sentence) - 1):
                current_keywords = keywords_per_sentence[i]
                next_keywords = keywords_per_sentence[i + 1]
                
                if current_keywords and next_keywords:
                    intersection = len(current_keywords.intersection(next_keywords))
                    union = len(current_keywords.union(next_keywords))
                    overlap = intersection / union if union > 0 else 0
                    overlaps.append(overlap)
            
            if overlaps:
                analysis.topic_consistency = (sum(overlaps) / len(overlaps)) * 10
        
        # Logical flow (simplified - could be enhanced with NLP)
        analysis.logical_flow = (analysis.transition_score + analysis.topic_consistency) / 2
        
        # Section connectivity (placeholder - would need section context)
        analysis.section_connectivity = 5.0  # Default neutral score
        
        return analysis
    
    async def review_with_llm(self, text: str, review_type: str, model: str = None) -> Dict:
        """Get LLM review for specific aspect"""
        if not model:
            model = self.config.get('review_model', 'llama3.1:latest')
        
        if review_type not in self.review_prompts:
            raise ValueError(f"Unknown review type: {review_type}")
        
        prompt = f"{self.review_prompts[review_type]}\n\nText to review:\n{text}"
        
        try:
            response = requests.post(
                f"{self.config['base_url']}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.get('api_key', '')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to parse JSON response
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback: extract JSON from text
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    else:
                        # Return structured fallback
                        return {
                            "score": 5,
                            "feedback": [content],
                            "suggestions": ["Manual review needed"]
                        }
            else:
                raise Exception(f"LLM API error: {response.status_code}")
                
        except Exception as e:
            print(f"LLM review error: {e}")
            return {
                "score": 0,
                "feedback": [f"Review failed: {str(e)}"],
                "suggestions": ["Manual review required"]
            }
    
    def analyze_comments_interactive(self, comments: List[str], parent_window=None) -> List[CommentReview]:
        """Analyze document comments interactively with user and LLM"""
        comment_reviews = []
        
        for i, comment in enumerate(comments):
            if not comment.strip():
                continue
            
            # Get LLM analysis of the comment
            llm_analysis = self._get_comment_analysis(comment)
            
            # Create comment review object
            review = CommentReview(
                original_comment=comment,
                llm_analysis=llm_analysis.get('analysis', 'No analysis available'),
                suggested_action=llm_analysis.get('suggested_action', 'review'),
                confidence_score=llm_analysis.get('confidence', 0.5)
            )
            
            # Interactive user decision
            user_choice = self._prompt_user_comment_decision(comment, llm_analysis, parent_window)
            review.user_decision = user_choice
            
            if user_choice == 'revise':
                # Generate revised content based on comment
                revised_content = self._generate_revised_content(comment, llm_analysis)
                review.revised_content = revised_content
            
            comment_reviews.append(review)
        
        return comment_reviews
    
    def _get_comment_analysis(self, comment: str) -> Dict:
        """Get LLM analysis of a specific comment"""
        prompt = f"""
        Analyze this document comment and provide guidance:
        
        Comment: "{comment}"
        
        Provide a JSON response with:
        {{
            "analysis": "What the comment is asking for",
            "suggested_action": "accept|revise|clarify|remove",
            "revision_approach": "How to address the comment",
            "confidence": <0.0-1.0>,
            "complexity": "low|medium|high"
        }}
        """
        
        try:
            response = requests.post(
                f"{self.config['base_url']}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.get('api_key', '')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.get('comment_model', 'llama3.1:latest'),
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1000
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                try:
                    return json.loads(content)
                except:
                    return {
                        "analysis": content,
                        "suggested_action": "review",
                        "confidence": 0.5
                    }
        except:
            pass
        
        return {
            "analysis": "Could not analyze comment",
            "suggested_action": "review",
            "confidence": 0.0
        }
    
    def _prompt_user_comment_decision(self, comment: str, llm_analysis: Dict, parent_window) -> str:
        """Prompt user for decision on how to handle a comment"""
        from tkinter import messagebox
        
        analysis_text = llm_analysis.get('analysis', 'No analysis')
        suggested_action = llm_analysis.get('suggested_action', 'review')
        
        message = f"Comment: {comment[:100]}{'...' if len(comment) > 100 else ''}\n\n"
        message += f"LLM Analysis: {analysis_text}\n\n"
        message += f"Suggested Action: {suggested_action}\n\n"
        message += "How would you like to handle this comment?\n\n"
        message += "Accept: Use LLM suggestion as-is\n"
        message += "Revise: Generate new content based on comment\n"
        message += "Skip: Ignore this comment\n"
        message += "Manual: Handle manually later"
        
        # Custom dialog for comment decision
        decision_window = tk.Toplevel(parent_window if parent_window else None)
        decision_window.title("Comment Review")
        decision_window.geometry("600x400")
        decision_window.configure(bg="#2b2b2b")
        
        # Comment display
        text_widget = tk.Text(decision_window, wrap=tk.WORD, height=15, width=70,
                             bg="#1e1e1e", fg="#ffffff", font=("Consolas", 10))
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(pady=10)
        
        # Decision variable
        decision = tk.StringVar(value="skip")
        
        # Buttons frame
        button_frame = tk.Frame(decision_window, bg="#2b2b2b")
        button_frame.pack(pady=10)
        
        def make_decision(choice):
            decision.set(choice)
            decision_window.destroy()
        
        tk.Button(button_frame, text="Accept", bg="#4CAF50", fg="white",
                 command=lambda: make_decision("accept")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Revise", bg="#2196F3", fg="white",
                 command=lambda: make_decision("revise")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Skip", bg="#FF9800", fg="white",
                 command=lambda: make_decision("skip")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Manual", bg="#9E9E9E", fg="white",
                 command=lambda: make_decision("manual")).pack(side=tk.LEFT, padx=5)
        
        # Wait for decision
        decision_window.wait_window()
        return decision.get()
    
    def _generate_revised_content(self, comment: str, llm_analysis: Dict) -> str:
        """Generate revised content based on comment"""
        revision_approach = llm_analysis.get('revision_approach', 'Address the comment')
        
        prompt = f"""
        Based on this comment and analysis, generate improved content:
        
        Comment: "{comment}"
        Analysis: {llm_analysis.get('analysis', '')}
        Approach: {revision_approach}
        
        Generate clear, well-written content that addresses the comment.
        Keep it concise and technically accurate.
        """
        
        try:
            response = requests.post(
                f"{self.config['base_url']}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.get('api_key', '')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.get('comment_model', 'llama3.1:latest'),
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "max_tokens": 1500
                },
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
        except:
            pass
        
        return f"[Generated content based on comment: {comment}]"
    
    def generate_comprehensive_report(self, text: str, section_path: str = "") -> Dict:
        """Generate comprehensive technical writing review report"""
        report = {
            'section_path': section_path,
            'timestamp': datetime.now().isoformat(),
            'text_length': len(text),
            'word_count': len(text.split()),
            'analyses': {}
        }
        
        # Tense analysis
        tense_analysis = self.analyze_tense_consistency(text)
        report['analyses']['tense_consistency'] = {
            'dominant_tense': tense_analysis.dominant_tense,
            'consistency_score': tense_analysis.consistency_score,
            'inconsistent_sentences': tense_analysis.inconsistent_sentences,
            'tense_distribution': {
                'past': tense_analysis.past_count,
                'present': tense_analysis.present_count,
                'future': tense_analysis.future_count
            }
        }
        
        # Readability metrics
        readability = self.calculate_readability_metrics(text)
        report['analyses']['readability'] = {
            'flesch_score': readability.flesch_score,
            'grade_level': readability.grade_level,
            'avg_sentence_length': readability.avg_sentence_length,
            'complex_word_ratio': readability.complex_word_ratio,
            'passive_voice_ratio': readability.passive_voice_ratio
        }
        
        # Coherence analysis
        coherence = self.analyze_coherence(text)
        report['analyses']['coherence'] = {
            'transition_score': coherence.transition_score,
            'topic_consistency': coherence.topic_consistency,
            'logical_flow': coherence.logical_flow
        }
        
        # Calculate overall scores
        scores = []
        if 'tense_consistency' in report['analyses']:
            scores.append(report['analyses']['tense_consistency']['consistency_score'])
        if 'coherence' in report['analyses']:
            scores.append(report['analyses']['coherence']['logical_flow'])
        
        # Add readability-based score
        flesch = readability.flesch_score
        readability_score = min(10, max(1, (flesch - 30) / 7))  # Scale 30-100 Flesch to 1-10
        scores.append(readability_score)
        
        report['overall_score'] = sum(scores) / len(scores) if scores else 5.0
        report['recommendation'] = self._get_overall_recommendation(report)
        
        return report
    
    def _get_overall_recommendation(self, report: Dict) -> str:
        """Generate overall recommendation based on analysis"""
        overall_score = report['overall_score']
        issues = []
        
        # Check tense consistency
        tense_score = report['analyses'].get('tense_consistency', {}).get('consistency_score', 10)
        if tense_score < 7:
            issues.append("improve tense consistency")
        
        # Check readability
        flesch_score = report['analyses'].get('readability', {}).get('flesch_score', 50)
        if flesch_score < 40:
            issues.append("simplify language for better readability")
        
        # Check coherence
        coherence_score = report['analyses'].get('coherence', {}).get('logical_flow', 5)
        if coherence_score < 6:
            issues.append("enhance logical flow and transitions")
        
        if overall_score >= 8:
            return "Excellent technical writing quality. Minor refinements may be beneficial."
        elif overall_score >= 6:
            recommendation = "Good technical writing with room for improvement. Consider: "
            return recommendation + ", ".join(issues) + "."
        else:
            recommendation = "Significant improvements needed. Priority areas: "
            return recommendation + ", ".join(issues) + "."
