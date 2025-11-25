"""
Service Container for Dependency Injection
Provides access to all service implementations.
"""
from typing import Optional
from app.application.services.profile_service import IProfileService
from app.application.services.job_ingestion_service import IJobIngestionService
from app.application.services.matching_engine import IMatchingEngine
from app.application.services.document_service import IDocumentService
from app.application.services.analytics_service import IAnalyticsService

class ServiceContainer:
    def __init__(
        self,
        profile_service: IProfileService,
        job_service: IJobIngestionService,
        matching_engine: IMatchingEngine,
        document_service: IDocumentService,
        analytics_service: IAnalyticsService
    ):
        self.profile_service = profile_service
        self.job_service = job_service
        self.matching_engine = matching_engine
        self.document_service = document_service
        self.analytics_service = analytics_service
