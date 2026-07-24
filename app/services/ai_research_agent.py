import json
from typing import Any, Dict, List
from openai import AsyncOpenAI
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ai_agent import AIResearchTask, AIGeneratedContent
# Assuming an AI provider client would be imported here, e.g., from google.generativeai or openai

class AIResearchAgent:
    """Autonomous agent for researching financial topics and generating blog drafts."""
    
    def __init__(self):
        from app.core.settings import settings
        self.provider = "qwen"
        self.client = AsyncOpenAI(
            api_key=settings.qwen_api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "qwen-turbo"

    async def run_daily_research(self, db: AsyncSession) -> None:
        """Runs daily — finds trending topics, generates blog drafts."""
        topics = await self._discover_trending_topics()
        
        for topic in topics:
            # Create a research task
            task = AIResearchTask(
                topic=topic,
                status="in_progress"
            )
            db.add(task)
            await db.commit()
            await db.refresh(task)
            
            try:
                research_data = await self._deep_research(topic)
                
                # Update task with research data
                task.results = research_data
                task.keywords = research_data.get("keywords", [])
                
                # Generate content
                draft_content = await self._generate_blog_draft(topic, research_data)
                
                # Save draft for admin approval
                draft = AIGeneratedContent(
                    research_task_id=task.id,
                    title=draft_content.get("title", topic),
                    content=draft_content.get("content", ""),
                    meta_title=draft_content.get("meta_title"),
                    meta_description=draft_content.get("meta_description"),
                    status="pending_approval"
                )
                db.add(draft)
                
                task.status = "completed"
                await db.commit()
                
            except Exception as e:
                task.status = "failed"
                task.error_message = str(e)
                await db.commit()

    async def _discover_trending_topics(self) -> List[str]:
        """Uses AI to find trending finance topics relevant to our audience."""
        prompt = "You are a financial content strategist. Suggest 3 trending, highly searchable finance topics for blog posts. Return ONLY a JSON list of strings, like [\"topic 1\", \"topic 2\"]."
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            # Best effort to strip markdown if not returning clean json
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            return json.loads(content)
        except Exception as e:
            print(f"Error discovering topics: {e}")
            return ["How to Calculate ROI on Rental Properties", "Tax Implications of Freelance Income", "The 50/30/20 Budgeting Rule Explained"]

    async def _deep_research(self, topic: str) -> Dict[str, Any]:
        """Gathers data, statistics, expert opinions on the topic."""
        prompt = f"""Conduct deep research on the topic: '{topic}'
Return ONLY a JSON object with this exact structure:
{{
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "statistics": ["stat 1", "stat 2"],
    "faqs": ["Q: ... A: ...", "Q: ... A: ..."]
}}
"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial researcher. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in deep research: {e}")
            return {
                "keywords": ["ROI", "rental property", "real estate investing"],
                "statistics": ["Average rental yield is 5-8%"],
                "faqs": ["What is a good ROI?", "How do I calculate cash flow?"]
            }

    async def _generate_blog_draft(self, topic: str, research: Dict[str, Any]) -> Dict[str, str]:
        """Generates SEO-optimized blog post draft."""
        prompt = f"""Write a comprehensive, highly engaging, SEO-optimized blog post about '{topic}'.
Use the following research:
Keywords: {', '.join(research.get('keywords', []))}
Statistics: {'; '.join(research.get('statistics', []))}
FAQs: {'; '.join(research.get('faqs', []))}

Format the blog post in Markdown. 
Return ONLY a JSON object with this exact structure:
{{
    "title": "A catchy, SEO-friendly title",
    "meta_title": "Title under 60 chars",
    "meta_description": "Description under 150 chars",
    "content": "# Your Markdown Content Here..."
}}
"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert financial blog writer and SEO specialist. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating draft: {e}")
            return {
                "title": f"The Ultimate Guide: {topic}",
                "meta_title": f"{topic} | FinanceCalculator",
                "meta_description": f"Learn everything you need to know about {topic}. Comprehensive guide with statistics and FAQs.",
                "content": f"# The Ultimate Guide: {topic}\n\nHere is a detailed breakdown based on our latest research...\n\n## Statistics\n{research.get('statistics', ['Average rental yield is 5-8%'])}\n\n## FAQs\n{research.get('faqs', ['What is a good ROI?'])}"
            }
