from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class UserProfile(BaseModel):
    role: str = "Belirlenmedi"
    experienceYears: int = 0
    skills: Dict[str, Any] = Field(default_factory=dict)
    languages: Dict[str, Any] = Field(default_factory=dict)
    avatarUrl: Optional[str] = None

class UserRPGState(BaseModel):
    level: int = 1
    xp: int = 0
    next_level_xp: int = 1000
    title: str = "Novice Seeker"
    energy: int = 100
    focus: int = 100
    max_energy: int = 100
    max_focus: int = 100

class UserDoc(BaseModel):
    userId: str
    email: str
    displayName: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    profile: UserProfile = Field(default_factory=UserProfile)
    rpgState: UserRPGState = Field(default_factory=UserRPGState)
    level: int = 1
    xp: int = 0
    next_level_xp: int = 1000

    class Config:
        extra = "allow" # allow extra fields for flexible DB documents


class SimulationNode(BaseModel):
    node_id: str
    parent: Optional[str] = None
    decision_name: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    description: str
    milestones: List[str] = Field(default_factory=list)
    agent_reasoning: Optional[str] = None
    is_terminal: bool = False

class SimulationDoc(BaseModel):
    simulation_id: str
    user_id: str
    initial_target: str
    nodes: List[SimulationNode] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    class Config:
        extra = "allow"


class QuestDoc(BaseModel):
    quest_id: str
    title: str
    description: str
    category: str = "Genel"
    xp_reward: int
    status: str = "pending" # pending, completed, failed
    verified_by: str = "manual"
    resource_link: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    completed_at: Optional[str] = None

    class Config:
        extra = "allow"


class LibraryResourceDoc(BaseModel):
    resource_id: str
    title: str
    platform: str
    url: str
    thumbnail_url: Optional[str] = None
    skill_tags: List[str] = Field(default_factory=list)
    status: str = "in_progress" # in_progress, completed
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    completed_at: Optional[str] = None

    class Config:
        extra = "allow"


class SkillNodeDoc(BaseModel):
    skill_id: str
    name: str
    level: int = 1
    xp: int = 0
    next_level_xp: int = 100
    category: str
    max_level: int = 5
    prerequisites: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    is_unlocked: bool = False
    status: str = "locked" # locked, available, learning, mastered

    class Config:
        extra = "allow"


class AnalyticsEventDoc(BaseModel):
    event_id: str
    type: str # e.g. xp_gain, quest_complete, simulation_branch
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    details: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"
