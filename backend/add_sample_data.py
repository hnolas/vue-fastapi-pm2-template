import asyncio
import datetime
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import async_session
from app.models.participant import Participant
from app.models.message import MessageContent, Message

async def create_sample_data():
    """Add sample data to the database for testing"""
    
    async with async_session() as db:
        # First check if we already have participants
        result = await db.execute(select(func.count()).select_from(Participant))
        count = result.scalar()
        
        if count > 0:
            print(f"Database already has {count} participants, skipping participant creation")
        else:
            print("Creating sample participants...")
            
            # Sample participants with different study groups
            participants = [
                Participant(
                    pid="VET001",
                    friendly_name="John Doe",
                    phone_number="+15551234567",
                    study_group="Intervention",
                    start_date=datetime.date.today(),
                    sms_window_start=datetime.time(9, 0),
                    sms_window_end=datetime.time(17, 0),
                    timezone_offset=-4,
                    active=True
                ),
                Participant(
                    pid="VET002",
                    friendly_name="Jane Smith",
                    phone_number="+15552345678",
                    study_group="Control",
                    start_date=datetime.date.today() - datetime.timedelta(days=7),
                    sms_window_start=datetime.time(8, 0),
                    sms_window_end=datetime.time(20, 0),
                    timezone_offset=-5,
                    active=True
                ),
                Participant(
                    pid="VET003",
                    friendly_name="Bob Williams",
                    phone_number="+15553456789",
                    study_group="Intervention",
                    start_date=datetime.date.today() - datetime.timedelta(days=14),
                    sms_window_start=datetime.time(10, 0),
                    sms_window_end=datetime.time(18, 0),
                    timezone_offset=-7,
                    active=True
                ),
                Participant(
                    pid="VET004",
                    friendly_name="Sarah Johnson",
                    phone_number="+15554567890",
                    study_group="Control",
                    start_date=datetime.date.today() - datetime.timedelta(days=21),
                    sms_window_start=datetime.time(7, 0),
                    sms_window_end=datetime.time(19, 0),
                    timezone_offset=-6,
                    active=False
                ),
            ]
            
            db.add_all(participants)
            await db.commit()
        
        # Check if we already have message templates
        result = await db.execute(select(func.count()).select_from(MessageContent))
        count = result.scalar()
        
        if count > 0:
            print(f"Database already has {count} message templates, skipping template creation")
        else:
            print("Creating sample message templates...")
            
            message_contents = [
                MessageContent(
                    content="Remember to track your steps today using your Fitbit! Every step counts.",
                    bucket="reminders",
                    active=True
                ),
                MessageContent(
                    content="Great job reaching your activity goal yesterday! Keep up the good work!",
                    bucket="encouragement",
                    active=True
                ),
                MessageContent(
                    content="Try to take a short walk during your lunch break today - even 10 minutes helps!",
                    bucket="suggestions",
                    active=True
                ),
                MessageContent(
                    content="Did you know? Regular physical activity can help manage prediabetes by improving how your body uses insulin.",
                    bucket="education",
                    active=True
                ),
                MessageContent(
                    content="Your weekly activity summary is now available. Check your Fitbit app to see your progress!",
                    bucket="reminders",
                    active=True
                ),
            ]
            
            db.add_all(message_contents)
            await db.commit()
        
        # Check if we already have message history
        result = await db.execute(select(func.count()).select_from(Message))
        count = result.scalar()
        
        if count > 0:
            print(f"Database already has {count} messages, skipping message history creation")
        else:
            print("Creating sample message history...")
            
            result = await db.execute(select(Participant))
            participants = result.scalars().all()
            
            result = await db.execute(select(MessageContent))
            message_contents = result.scalars().all()
            
            if participants and message_contents:
                now = datetime.datetime.now()
                
                for participant in participants:
                    if participant.active:
                        num_messages = random.randint(3, 8)
                        
                        for _ in range(num_messages):
                            days_ago = random.randint(0, 7)
                            hours_ago = random.randint(0, 23)
                            minutes_ago = random.randint(0, 59)
                            
                            sent_time = now - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                            
                            message_content = random.choice(message_contents)
                            
                            status_options = ["delivered"] * 7 + ["sent"] * 2 + ["failed"] * 1
                            status = random.choice(status_options)
                            
                            delivered_time = sent_time + datetime.timedelta(minutes=random.randint(1, 5)) if status == "delivered" else None
                            error = "Failed to deliver: recipient unavailable" if status == "failed" else None
                            
                            message = Message(
                                participant_id=participant.id,
                                content_id=message_content.id,
                                content=message_content.content,
                                bucket=message_content.bucket,
                                status=status,
                                sent_datetime=sent_time,
                                delivered_datetime=delivered_time,
                                twilio_sid=f"SM{random.randint(10000000, 99999999)}" if status != "failed" else None,
                                error=error
                            )
                            
                            db.add(message)
                
                await db.commit()
                print(f"Created sample message history successfully!")
            else:
                print("Cannot create message history: no participants or message templates found")
        
        print("Sample data creation completed!")

if __name__ == "__main__":
    asyncio.run(create_sample_data())
