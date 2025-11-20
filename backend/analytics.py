"""
Analytics and Metrics Module for DocumentFiller v3.1
Provides comprehensive analytics and usage tracking
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from database import (
    UserModel, DocumentModel, GenerationHistoryModel,
    ReviewHistoryModel, SessionModel, get_db
)
import json

class AnalyticsService:
    """Service for generating analytics and metrics"""

    def __init__(self, db: Session):
        self.db = db

    # User Analytics

    def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        """Get comprehensive user statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Document stats
        total_documents = self.db.query(DocumentModel).filter(
            DocumentModel.user_id == user_id
        ).count()

        recent_documents = self.db.query(DocumentModel).filter(
            and_(
                DocumentModel.user_id == user_id,
                DocumentModel.created_at >= cutoff_date
            )
        ).count()

        # Generation stats
        total_generations = self.db.query(GenerationHistoryModel).join(
            DocumentModel
        ).filter(
            DocumentModel.user_id == user_id
        ).count()

        recent_generations = self.db.query(GenerationHistoryModel).join(
            DocumentModel
        ).filter(
            and_(
                DocumentModel.user_id == user_id,
                GenerationHistoryModel.created_at >= cutoff_date
            )
        ).count()

        # Model usage breakdown
        model_usage = self.db.query(
            GenerationHistoryModel.model,
            func.count(GenerationHistoryModel.id).label('count')
        ).join(DocumentModel).filter(
            and_(
                DocumentModel.user_id == user_id,
                GenerationHistoryModel.created_at >= cutoff_date
            )
        ).group_by(GenerationHistoryModel.model).all()

        # Token usage
        total_tokens = self.db.query(
            func.sum(GenerationHistoryModel.tokens_used)
        ).join(DocumentModel).filter(
            DocumentModel.user_id == user_id
        ).scalar() or 0

        recent_tokens = self.db.query(
            func.sum(GenerationHistoryModel.tokens_used)
        ).join(DocumentModel).filter(
            and_(
                DocumentModel.user_id == user_id,
                GenerationHistoryModel.created_at >= cutoff_date
            )
        ).scalar() or 0

        # Average generation time
        avg_generation_time = self.db.query(
            func.avg(GenerationHistoryModel.generation_time)
        ).join(DocumentModel).filter(
            and_(
                DocumentModel.user_id == user_id,
                GenerationHistoryModel.created_at >= cutoff_date
            )
        ).scalar() or 0

        # Review stats
        total_reviews = self.db.query(ReviewHistoryModel).join(
            DocumentModel
        ).filter(
            DocumentModel.user_id == user_id
        ).count()

        recent_reviews = self.db.query(ReviewHistoryModel).join(
            DocumentModel
        ).filter(
            and_(
                DocumentModel.user_id == user_id,
                ReviewHistoryModel.created_at >= cutoff_date
            )
        ).count()

        # Average quality score
        avg_quality_score = self.db.query(
            func.avg(ReviewHistoryModel.overall_score)
        ).join(DocumentModel).filter(
            and_(
                DocumentModel.user_id == user_id,
                ReviewHistoryModel.created_at >= cutoff_date
            )
        ).scalar() or 0

        return {
            'period_days': days,
            'documents': {
                'total': total_documents,
                'recent': recent_documents
            },
            'generations': {
                'total': total_generations,
                'recent': recent_generations,
                'avg_time_seconds': float(avg_generation_time) if avg_generation_time else 0
            },
            'tokens': {
                'total': int(total_tokens),
                'recent': int(recent_tokens),
                'avg_per_generation': int(recent_tokens / recent_generations) if recent_generations > 0 else 0
            },
            'reviews': {
                'total': total_reviews,
                'recent': recent_reviews,
                'avg_quality_score': float(avg_quality_score) if avg_quality_score else 0
            },
            'model_usage': [
                {'model': model, 'count': count}
                for model, count in model_usage
            ]
        }

    def get_user_activity_timeline(
        self,
        user_id: int,
        days: int = 30,
        granularity: str = 'day'
    ) -> List[Dict]:
        """Get user activity timeline (daily/hourly breakdown)"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        if granularity == 'hour':
            date_format = '%Y-%m-%d %H:00:00'
        else:  # day
            date_format = '%Y-%m-%d'

        # Query generations by time period
        activity = self.db.query(
            func.strftime(date_format, GenerationHistoryModel.created_at).label('period'),
            func.count(GenerationHistoryModel.id).label('generations'),
            func.sum(GenerationHistoryModel.tokens_used).label('tokens')
        ).join(DocumentModel).filter(
            and_(
                DocumentModel.user_id == user_id,
                GenerationHistoryModel.created_at >= cutoff_date
            )
        ).group_by('period').order_by('period').all()

        return [
            {
                'period': period,
                'generations': generations,
                'tokens': int(tokens) if tokens else 0
            }
            for period, generations, tokens in activity
        ]

    def get_user_document_breakdown(self, user_id: int) -> Dict:
        """Get breakdown of user's documents by status and type"""
        documents = self.db.query(DocumentModel).filter(
            DocumentModel.user_id == user_id
        ).all()

        total = len(documents)

        # Status breakdown
        status_counts = {}
        for doc in documents:
            metadata = json.loads(doc.metadata) if doc.metadata else {}
            status = metadata.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Section count distribution
        section_distribution = {}
        for doc in documents:
            section_count = doc.section_count or 0
            bucket = f"{(section_count // 5) * 5}-{((section_count // 5) + 1) * 5}"
            section_distribution[bucket] = section_distribution.get(bucket, 0) + 1

        # Average sections per document
        avg_sections = sum(doc.section_count or 0 for doc in documents) / total if total > 0 else 0

        return {
            'total_documents': total,
            'status_breakdown': status_counts,
            'section_distribution': section_distribution,
            'avg_sections_per_document': round(avg_sections, 2)
        }

    # System-wide Analytics

    def get_system_stats(self, days: int = 30) -> Dict:
        """Get system-wide statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # User stats
        total_users = self.db.query(UserModel).count()
        active_users = self.db.query(func.count(func.distinct(DocumentModel.user_id))).filter(
            DocumentModel.created_at >= cutoff_date
        ).scalar() or 0

        # Document stats
        total_documents = self.db.query(DocumentModel).count()
        recent_documents = self.db.query(DocumentModel).filter(
            DocumentModel.created_at >= cutoff_date
        ).count()

        # Generation stats
        total_generations = self.db.query(GenerationHistoryModel).count()
        recent_generations = self.db.query(GenerationHistoryModel).filter(
            GenerationHistoryModel.created_at >= cutoff_date
        ).count()

        # Token usage
        total_tokens = self.db.query(
            func.sum(GenerationHistoryModel.tokens_used)
        ).scalar() or 0

        recent_tokens = self.db.query(
            func.sum(GenerationHistoryModel.tokens_used)
        ).filter(
            GenerationHistoryModel.created_at >= cutoff_date
        ).scalar() or 0

        # Model popularity
        model_usage = self.db.query(
            GenerationHistoryModel.model,
            func.count(GenerationHistoryModel.id).label('count'),
            func.sum(GenerationHistoryModel.tokens_used).label('tokens')
        ).filter(
            GenerationHistoryModel.created_at >= cutoff_date
        ).group_by(GenerationHistoryModel.model).all()

        # Average quality scores
        avg_quality = self.db.query(
            func.avg(ReviewHistoryModel.overall_score)
        ).filter(
            ReviewHistoryModel.created_at >= cutoff_date
        ).scalar() or 0

        return {
            'period_days': days,
            'users': {
                'total': total_users,
                'active': active_users,
                'activity_rate': round(active_users / total_users * 100, 2) if total_users > 0 else 0
            },
            'documents': {
                'total': total_documents,
                'recent': recent_documents
            },
            'generations': {
                'total': total_generations,
                'recent': recent_generations,
                'per_active_user': round(recent_generations / active_users, 2) if active_users > 0 else 0
            },
            'tokens': {
                'total': int(total_tokens),
                'recent': int(recent_tokens),
                'per_generation': int(recent_tokens / recent_generations) if recent_generations > 0 else 0
            },
            'model_usage': [
                {
                    'model': model,
                    'count': count,
                    'tokens': int(tokens) if tokens else 0,
                    'avg_tokens': int(tokens / count) if count > 0 and tokens else 0
                }
                for model, count, tokens in model_usage
            ],
            'quality': {
                'avg_score': round(float(avg_quality), 2) if avg_quality else 0
            }
        }

    def get_top_users(self, metric: str = 'generations', limit: int = 10, days: int = 30) -> List[Dict]:
        """Get top users by various metrics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        if metric == 'generations':
            query = self.db.query(
                UserModel.id,
                UserModel.username,
                UserModel.email,
                func.count(GenerationHistoryModel.id).label('value')
            ).join(DocumentModel, UserModel.id == DocumentModel.user_id).join(
                GenerationHistoryModel, DocumentModel.id == GenerationHistoryModel.document_id
            ).filter(
                GenerationHistoryModel.created_at >= cutoff_date
            ).group_by(UserModel.id).order_by(func.count(GenerationHistoryModel.id).desc())

        elif metric == 'tokens':
            query = self.db.query(
                UserModel.id,
                UserModel.username,
                UserModel.email,
                func.sum(GenerationHistoryModel.tokens_used).label('value')
            ).join(DocumentModel, UserModel.id == DocumentModel.user_id).join(
                GenerationHistoryModel, DocumentModel.id == GenerationHistoryModel.document_id
            ).filter(
                GenerationHistoryModel.created_at >= cutoff_date
            ).group_by(UserModel.id).order_by(func.sum(GenerationHistoryModel.tokens_used).desc())

        elif metric == 'documents':
            query = self.db.query(
                UserModel.id,
                UserModel.username,
                UserModel.email,
                func.count(DocumentModel.id).label('value')
            ).join(DocumentModel, UserModel.id == DocumentModel.user_id).filter(
                DocumentModel.created_at >= cutoff_date
            ).group_by(UserModel.id).order_by(func.count(DocumentModel.id).desc())

        else:
            raise ValueError(f"Unknown metric: {metric}")

        results = query.limit(limit).all()

        return [
            {
                'user_id': user_id,
                'username': username,
                'email': email,
                'value': int(value) if value else 0,
                'metric': metric
            }
            for user_id, username, email, value in results
        ]

    # Performance Analytics

    def get_performance_metrics(self, days: int = 7) -> Dict:
        """Get system performance metrics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Generation performance
        generations = self.db.query(GenerationHistoryModel).filter(
            GenerationHistoryModel.created_at >= cutoff_date
        ).all()

        if not generations:
            return {
                'period_days': days,
                'sample_size': 0,
                'generation_time': {},
                'token_throughput': {},
                'error_rate': 0
            }

        generation_times = [g.generation_time for g in generations if g.generation_time]
        tokens_per_second = [
            g.tokens_used / g.generation_time
            for g in generations
            if g.generation_time and g.generation_time > 0 and g.tokens_used
        ]

        successful = sum(1 for g in generations if not g.error)
        failed = len(generations) - successful

        return {
            'period_days': days,
            'sample_size': len(generations),
            'generation_time': {
                'min': round(min(generation_times), 2) if generation_times else 0,
                'max': round(max(generation_times), 2) if generation_times else 0,
                'avg': round(sum(generation_times) / len(generation_times), 2) if generation_times else 0,
                'median': round(sorted(generation_times)[len(generation_times) // 2], 2) if generation_times else 0
            },
            'token_throughput': {
                'min': round(min(tokens_per_second), 2) if tokens_per_second else 0,
                'max': round(max(tokens_per_second), 2) if tokens_per_second else 0,
                'avg': round(sum(tokens_per_second) / len(tokens_per_second), 2) if tokens_per_second else 0
            },
            'error_rate': round(failed / len(generations) * 100, 2) if generations else 0,
            'success_count': successful,
            'failure_count': failed
        }

    # Quality Analytics

    def get_quality_trends(self, days: int = 30) -> Dict:
        """Get document quality trends over time"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        reviews = self.db.query(ReviewHistoryModel).filter(
            ReviewHistoryModel.created_at >= cutoff_date
        ).all()

        if not reviews:
            return {
                'period_days': days,
                'sample_size': 0,
                'overall_quality': {},
                'metric_averages': {}
            }

        overall_scores = [r.overall_score for r in reviews if r.overall_score]

        # Extract specific metrics from review data
        tense_scores = []
        readability_scores = []
        coherence_scores = []

        for review in reviews:
            if review.metrics:
                try:
                    metrics = json.loads(review.metrics) if isinstance(review.metrics, str) else review.metrics
                    if 'tense_consistency' in metrics:
                        tense_scores.append(metrics['tense_consistency'].get('consistency_score', 0))
                    if 'readability' in metrics:
                        readability_scores.append(metrics['readability'].get('flesch_score', 0))
                    if 'coherence' in metrics:
                        coherence_scores.append(metrics['coherence'].get('logical_flow', 0))
                except:
                    pass

        return {
            'period_days': days,
            'sample_size': len(reviews),
            'overall_quality': {
                'min': round(min(overall_scores), 2) if overall_scores else 0,
                'max': round(max(overall_scores), 2) if overall_scores else 0,
                'avg': round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else 0
            },
            'metric_averages': {
                'tense_consistency': round(sum(tense_scores) / len(tense_scores), 2) if tense_scores else 0,
                'readability': round(sum(readability_scores) / len(readability_scores), 2) if readability_scores else 0,
                'coherence': round(sum(coherence_scores) / len(coherence_scores), 2) if coherence_scores else 0
            },
            'distribution': {
                'excellent': sum(1 for s in overall_scores if s >= 8),
                'good': sum(1 for s in overall_scores if 6 <= s < 8),
                'needs_improvement': sum(1 for s in overall_scores if s < 6)
            }
        }

    # Export functionality

    def export_user_data(self, user_id: int, format: str = 'json') -> Dict:
        """Export all user data for download"""
        user_stats = self.get_user_stats(user_id, days=365)  # Full year
        user_activity = self.get_user_activity_timeline(user_id, days=90)  # Last 90 days
        user_breakdown = self.get_user_document_breakdown(user_id)

        export_data = {
            'exported_at': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'statistics': user_stats,
            'activity_timeline': user_activity,
            'document_breakdown': user_breakdown
        }

        if format == 'json':
            return export_data
        else:
            # Could add CSV, PDF export here
            return export_data
