"""
AI 摘要插件数据模型
"""
from datetime import datetime
from app import db


class PostAISummary(db.Model):
    """文章 AI 摘要缓存表"""
    __tablename__ = 'post_ai_summaries'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), unique=True, nullable=False, index=True)
    model = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PostAISummary post_id={self.post_id} model={self.model}>'
