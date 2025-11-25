# 📅 PHASE BREAKDOWN
## 12-Week Implementation Timeline

---

## 📋 **OVERVIEW**

This document breaks down the **6-phase Strangler Fig migration** into weekly deliverables with clear acceptance criteria, risk mitigation, and team assignments.

**Total Duration:** 12 weeks (3 months)  
**Team Size:** 1-2 developers (solo-friendly)  
**Work Pattern:** 20 hours/week (part-time)  
**Total Effort:** ~240 hours  

---

## 🎯 **PHASE SUMMARY**

| Phase | Duration | Focus | Risk |
|-------|----------|-------|------|
| **1. Infrastructure** | Weeks 1-2 | SQLite schema, migrations, repos | LOW |
| **2. Service Layer** | Weeks 3-5 | Extract business logic, Pydantic models | MEDIUM |
| **3. Event Bus** | Week 6 | In-memory queue, event schemas | LOW |
| **4. GUI Refactor** | Weeks 7-9 | Break monolith into 4 views | MEDIUM |
| **5. FastAPI Layer** | Weeks 10-11 | REST endpoints, auth, docs | LOW |
| **6. Testing & Polish** | Week 12 | 80% coverage, docs, release | LOW |

---

## 📆 **WEEK-BY-WEEK BREAKDOWN**

---

### **PHASE 1: INFRASTRUCTURE (Weeks 1-2)**

**Goal:** Establish database foundation with migrations, repositories, and data integrity.

---

#### **Week 1: Database Schema & Migration**

**Monday:**
- Create `app/infrastructure/database/migrations/` directory
- Implement `001_create_schema.py` (10 tables, indexes, constraints)
- Write schema verification tests

**Tuesday:**
- Execute schema migration against new `resume_toolkit.db`
- Verify all tables created with correct structure
- Test foreign key cascades manually (insert → delete → verify)

**Wednesday:**
- Implement `002_migrate_profiles.py` (JSON → SQLite)
- Write validation logic (compare row counts, spot-check data)
- Test migration with sample profile data

**Thursday:**
- Implement `003_migrate_csv_tracker.py` (CSV → SQLite)
- Parse 49-column tracker, split into 3 tables (job_postings, applications, match_scores)
- Handle missing/malformed data gracefully

**Friday:**
- Run full migration pipeline (schema → profiles → tracker)
- Execute post-migration validation checks
- Create timestamped backup of original JSON/CSV files
- **Acceptance Test:** All data migrated with 100% accuracy

**Weekend:**
- Document migration process in MIGRATION_PLAYBOOK.md
- Review and refine rollback procedures

**Deliverables:**
- ✅ 10 SQLite tables with data
- ✅ 3 migration scripts (001, 002, 003)
- ✅ Backup of original data
- ✅ Migration validation report

**Acceptance Criteria:**
- [ ] All 10 tables exist with correct schema
- [ ] Profile data matches JSON files (100% accuracy)
- [ ] CSV tracker migrated with all 49 columns preserved
- [ ] Foreign key constraints enforced
- [ ] Rollback script successfully restores original state

**Risk Mitigation:**
- **Risk:** Data loss during migration  
  **Mitigation:** Timestamped backups before each phase, rollback scripts tested

---

#### **Week 2: Repository Layer**

**Monday:**
- Create `app/infrastructure/database/sqlite_profile_repo.py`
- Implement `create_profile()`, `get_profile_by_id()`, `update_profile()`
- Write unit tests with in-memory SQLite database

**Tuesday:**
- Implement `add_experience()`, `get_experiences()`, `delete_experience()`
- Add support for experience bullets (nested inserts)
- Test CASCADE deletes (profile deletion removes experiences)

**Wednesday:**
- Create `app/infrastructure/database/sqlite_job_repo.py`
- Implement `create_job_posting()`, `get_job_by_id()`, `search_jobs()`
- Add filtering by company, role, location

**Thursday:**
- Create `app/infrastructure/database/sqlite_application_repo.py`
- Implement `create_application()`, `update_status()`, `get_applications_by_profile()`
- Add sorting by match score (DESC), date applied (DESC)

**Friday:**
- Integration tests for all repositories
- Test transaction rollback on errors
- Performance benchmarks (CRUD operations <50ms)
- **Acceptance Test:** All CRUD operations functional with <1% error rate

**Deliverables:**
- ✅ 3 repository classes (ProfileRepo, JobRepo, ApplicationRepo)
- ✅ 20+ repository methods
- ✅ Unit tests with 90%+ coverage
- ✅ Integration tests with real SQLite DB

**Acceptance Criteria:**
- [ ] All CRUD operations work correctly
- [ ] Foreign key relationships preserved
- [ ] Transactions rollback on errors
- [ ] Query performance <50ms for single records
- [ ] Batch operations handle 100+ records efficiently

---

### **PHASE 2: SERVICE LAYER (Weeks 3-5)**

**Goal:** Extract business logic from scripts into clean service interfaces with Pydantic validation.

---

#### **Week 3: ProfileService & Pydantic Models**

**Monday:**
- Create `app/domain/models.py` with Pydantic schemas
- Define `ProfileModel`, `ExperienceModel`, `SkillModel`, `EducationModel`
- Add validation rules (email format, required fields, length constraints)

**Tuesday:**
- Create `app/application/services/profile_service.py`
- Implement `IProfileService` interface (create, get, update, delete)
- Wire up ProfileRepo dependency injection

**Wednesday:**
- Implement `add_experience()` with bullet validation
- Add `get_skills()` with filtering by skill_type
- Implement `calculate_profile_strength()` (0-100 score based on completeness)

**Thursday:**
- Extract candidate summary generation from `profile_candidate.json` logic
- Implement `update_summary()` with keyword injection
- Add `export_to_json()` for backward compatibility

**Friday:**
- Write comprehensive unit tests (mock ProfileRepo)
- Test validation failures (invalid email, missing required fields)
- **Acceptance Test:** ProfileService handles all profile operations without errors

**Deliverables:**
- ✅ 10+ Pydantic models
- ✅ ProfileService with 8 methods
- ✅ Unit tests with 85%+ coverage
- ✅ Validation tests for all edge cases

**Acceptance Criteria:**
- [ ] All profile operations validated with Pydantic
- [ ] Service layer has no direct SQL queries (uses repo)
- [ ] Profile strength calculation accurate
- [ ] Backward compatible with JSON export

---

#### **Week 4: MatchingEngine (Preserve 8-Factor Algorithm)**

**Monday:**
- Extract logic from `scripts/04_match_engine.py`
- Create `app/application/services/matching_engine.py`
- Implement `IMatchingEngine` interface

**Tuesday:**
- Implement `compute_match()` preserving 8-factor weights (30-25-15-10-10-5-5)
- Return `MatchBreakdownModel` with all 8 scores + gaps + recommendations
- Add unit tests comparing old vs new algorithm (must match 100%)

**Wednesday:**
- Implement `rank_bullets_for_job()` (select top 6 bullets by keyword overlap)
- Add scoring logic (keyword matches +10, metrics +15, action verbs +10)
- Test with sample job descriptions

**Thursday:**
- Implement `suggest_skills_to_add()` (identify missing JD keywords)
- Add `generate_match_report()` (text summary with color coding)
- Test edge cases (low match, perfect match, no experience)

**Friday:**
- Integration tests with real profile + job data
- Benchmark performance (match computation <500ms)
- **Acceptance Test:** Match scores identical to legacy system

**Deliverables:**
- ✅ MatchingEngine with 8-factor algorithm
- ✅ 4 matching methods (compute, rank, suggest, report)
- ✅ Unit tests with 90%+ coverage
- ✅ Performance benchmarks <500ms

**Acceptance Criteria:**
- [ ] Match scores identical to `04_match_engine.py` output
- [ ] All 8 factors weighted correctly (30-25-15-10-10-5-5)
- [ ] Gap analysis identifies missing requirements
- [ ] Bullet ranking prioritizes keyword-rich bullets

---

#### **Week 5: JobIngestionService & DocumentService**

**Monday:**
- Create `app/application/services/job_ingestion_service.py`
- Implement `ingest_job_description()` (parse JD text, extract keywords)
- Use spaCy for NER, NLTK for keyword extraction

**Tuesday:**
- Implement `parse_requirements()` (extract years experience, education, skills)
- Add regex patterns for common JD formats
- Test with 10+ real job descriptions

**Wednesday:**
- Extract logic from `scripts/15_generate_jd_resume.py`
- Create `app/application/services/document_service.py`
- Implement `generate_resume()` with ATS optimization

**Thursday:**
- Implement `generate_cover_letter()` using template system
- Add `generate_ats_report()` (keyword density, formatting checks)
- Preserve document taxonomy routing (00_Incoming, 10_Materials, etc.)

**Friday:**
- Integration tests (ingest JD → compute match → generate resume)
- Verify DOCX output matches legacy format
- **Acceptance Test:** Generated documents pass ATS analyzers (>70% score)

**Deliverables:**
- ✅ JobIngestionService with JD parsing
- ✅ DocumentService with resume/cover letter generation
- ✅ ATS optimization preserved
- ✅ Integration tests for full workflow

**Acceptance Criteria:**
- [ ] Job descriptions parsed with 90%+ accuracy
- [ ] Resumes pass ATS checks (no tables, standard headers)
- [ ] Cover letters personalized with company research
- [ ] Document taxonomy routing functional

---

### **PHASE 3: EVENT BUS (Week 6)**

**Goal:** Implement in-memory event bus for decoupled communication between services.

---

#### **Week 6: Event Bus Implementation**

**Monday:**
- Create `app/infrastructure/event_bus/in_memory_bus.py`
- Implement `EventBus` class with `queue.Queue`
- Add `subscribe()`, `publish()`, `start()`, `stop()` methods

**Tuesday:**
- Define event schemas in `app/domain/events.py`
- Create `ProfileUpdatedEvent`, `JobIngestedEvent`, `MatchComputedEvent`, `ApplicationSubmittedEvent`, `DocumentGeneratedEvent`
- Add `BaseEvent` with timestamp, event_type, payload

**Wednesday:**
- Add event publishers to services
- ProfileService publishes `ProfileUpdatedEvent` on update
- MatchingEngine publishes `MatchComputedEvent` after scoring
- DocumentService publishes `DocumentGeneratedEvent` after generation

**Thursday:**
- Create analytics subscriber (consumes events, updates dashboard metrics)
- Implement background worker thread for event processing
- Add error handling (dead letter queue for failed events)

**Friday:**
- Integration tests (publish → queue → consume → handler execution)
- Test concurrent event publishing (10+ threads)
- **Acceptance Test:** Events processed within 100ms, zero loss

**Deliverables:**
- ✅ EventBus with in-memory queue
- ✅ 6 event schemas
- ✅ Event publishers in 3 services
- ✅ Analytics subscriber
- ✅ Unit + integration tests

**Acceptance Criteria:**
- [ ] Events published and consumed successfully
- [ ] No event loss under concurrent load
- [ ] Background worker processes events <100ms
- [ ] Error handling prevents crashes

---

### **PHASE 4: GUI REFACTOR (Weeks 7-9)**

**Goal:** Break 1715-line monolithic GUI into 4 modular views with dependency injection.

---

#### **Week 7: Extract ProfileView**

**Monday:**
- Create `app/presentation/gui/views/profile_view.py`
- Extract profile management UI (lines 1-400 of `simple_gui_modern.py`)
- Add profile form (name, email, phone, LinkedIn, GitHub, location)

**Tuesday:**
- Add experience management (list, add, edit, delete)
- Implement bullet editing with inline validation
- Wire up ProfileService via ServiceContainer

**Wednesday:**
- Add skills management (categorized by type: technical, soft, methodology)
- Implement skill autocomplete (suggest from taxonomy)
- Add education section

**Thursday:**
- Add profile strength indicator (animated progress bar 0-100%)
- Implement "Save Profile" button with validation feedback
- Add export to JSON (backward compatibility)

**Friday:**
- Unit tests for UI components (mock ProfileService)
- Integration test (full profile CRUD workflow)
- **Acceptance Test:** Profile management fully functional, no regressions

**Deliverables:**
- ✅ ProfileView module (300-400 lines)
- ✅ Profile CRUD UI with validation
- ✅ Profile strength indicator
- ✅ Tests with 80%+ coverage

**Acceptance Criteria:**
- [ ] All profile operations work via new view
- [ ] UI matches glassmorphic design (19.2:1 contrast)
- [ ] Form validation prevents invalid data
- [ ] Profile strength updates in real-time

---

#### **Week 8: Extract JobAnalysisView & AnalyticsDashboard**

**Monday:**
- Create `app/presentation/gui/views/job_analysis_view.py`
- Extract JD input area, match score display (lines 401-800)
- Add "Analyze Job" button wired to MatchingEngine

**Tuesday:**
- Implement match score breakdown (8 factors with AnimatedProgressBar)
- Add gap analysis section (bullet list of missing requirements)
- Display recommendations (skills to add, experiences to highlight)

**Wednesday:**
- Create `app/presentation/gui/views/analytics_dashboard.py`
- Extract metrics row (4 ModernMetricCards) from lines 1407-1707
- Add application tracker table (sortable columns, color-coded rows)

**Thursday:**
- Implement budget integration (load from CSV, calculate totals)
- Add charts (match score distribution, application timeline)
- Implement filters (date range, status, match score threshold)

**Friday:**
- Integration tests (ingest JD → display match → update analytics)
- Performance test (load 200+ applications in <2 seconds)
- **Acceptance Test:** Job analysis and analytics fully functional

**Deliverables:**
- ✅ JobAnalysisView module (250-300 lines)
- ✅ AnalyticsDashboard module (400-500 lines)
- ✅ Charts and visualizations
- ✅ Tests with 75%+ coverage

**Acceptance Criteria:**
- [ ] Match score calculated and displayed correctly
- [ ] Analytics dashboard loads 200+ apps <2s
- [ ] Budget data integrates without errors
- [ ] Filters work correctly (no UI freezing)

---

#### **Week 9: Extract PreferencesView & Integration**

**Monday:**
- Create `app/presentation/gui/views/preferences_view.py`
- Extract 16 preference options (lines 761-991)
- Add collapsible sections (Work Preferences, Salary, Notifications, API Keys)

**Tuesday:**
- Implement API key management (encrypted storage)
- Add "Test API Connection" buttons for Adzuna, Hugging Face
- Implement auto-save (save on change after 2-second debounce)

**Wednesday:**
- Create main application shell (`app/presentation/gui/main_window.py`)
- Implement tab navigation (Profile, Job Analysis, Analytics, Preferences)
- Wire up ServiceContainer for all views

**Thursday:**
- Integrate event bus (views subscribe to relevant events)
- Test inter-view communication (profile update → analytics refresh)
- Add keyboard shortcuts (Ctrl+G for generate, Ctrl+A for analytics)

**Friday:**
- End-to-end testing (full user workflow: create profile → ingest job → generate resume → view analytics)
- Accessibility audit (WCAG 2.1 AA compliance check)
- **Acceptance Test:** GUI fully modular, all features working

**Deliverables:**
- ✅ PreferencesView module (200-250 lines)
- ✅ Main application shell with tabs
- ✅ Event bus integration across views
- ✅ E2E tests for full workflow

**Acceptance Criteria:**
- [ ] All 4 views accessible via tabs
- [ ] Views communicate via event bus (no tight coupling)
- [ ] Keyboard navigation works correctly
- [ ] WCAG 2.1 AA compliance maintained (4.5:1 contrast minimum)

---

### **PHASE 5: FASTAPI LAYER (Weeks 10-11)**

**Goal:** Expose service layer via REST API with authentication, rate limiting, and OpenAPI docs.

---

#### **Week 10: API Foundation & Profile Endpoints**

**Monday:**
- Create `app/presentation/api/main.py` with FastAPI setup
- Configure CORS, rate limiting (slowapi), GZip compression
- Add health check endpoint (`GET /health`)

**Tuesday:**
- Implement JWT authentication
- Create `create_access_token()`, `verify_token()` dependency
- Add login endpoint (`POST /auth/login`)

**Wednesday:**
- Implement profile router (`app/presentation/api/routers/profile.py`)
- Add endpoints: POST /api/profiles, GET /{id}, PUT /{id}, POST /experiences
- Wire up ProfileService via dependency injection

**Thursday:**
- Add rate limiting to profile endpoints (5 req/min for POST)
- Implement Pydantic request/response models
- Write API tests with TestClient

**Friday:**
- Generate OpenAPI docs (Swagger UI at /api/docs)
- Test all profile endpoints with Postman/curl
- **Acceptance Test:** Profile API fully functional with auth

**Deliverables:**
- ✅ FastAPI app with 5 profile endpoints
- ✅ JWT authentication
- ✅ Rate limiting (5-10 req/min)
- ✅ OpenAPI docs

**Acceptance Criteria:**
- [ ] All profile endpoints return correct data
- [ ] JWT auth prevents unauthorized access
- [ ] Rate limiting blocks excessive requests
- [ ] OpenAPI docs render correctly

---

#### **Week 11: Job, Application, Document, Analytics Endpoints**

**Monday:**
- Implement job router (`app/presentation/api/routers/job.py`)
- Add endpoints: POST /ingest, GET /{id}, GET /, PATCH /{id}/status
- Add pagination for GET / (limit, offset)

**Tuesday:**
- Implement application router (`app/presentation/api/routers/application.py`)
- Add endpoints: POST /analyze (compute match), POST /rank-bullets, GET /suggestions
- Add rate limiting for expensive operations (5 req/min for analyze)

**Wednesday:**
- Implement document router (`app/presentation/api/routers/document.py`)
- Add endpoints: POST /resume, POST /cover-letter, GET /download/{filename}, POST /ats-analysis
- Add file download security (validate filename, prevent directory traversal)

**Thursday:**
- Implement analytics router (`app/presentation/api/routers/analytics.py`)
- Add endpoints: GET /dashboard, GET /history, GET /export/csv
- Add query params (days, limit, status filters)

**Friday:**
- E2E API tests (full workflow: create profile → ingest job → analyze → generate resume)
- Load testing (100 concurrent requests)
- **Acceptance Test:** All 15+ endpoints functional, <100ms latency

**Deliverables:**
- ✅ 4 additional routers (job, application, document, analytics)
- ✅ 15+ total endpoints
- ✅ E2E API tests
- ✅ Load testing report

**Acceptance Criteria:**
- [ ] All endpoints return correct data
- [ ] API handles 100 concurrent requests
- [ ] Response times <100ms (excluding document generation)
- [ ] Error responses follow REST conventions (4xx, 5xx)

---

### **PHASE 6: TESTING & POLISH (Week 12)**

**Goal:** Achieve 80% test coverage, finalize documentation, and prepare release.

---

#### **Week 12: Testing, Documentation, Release**

**Monday:**
- Run coverage report (`pytest --cov=app --cov-report=html`)
- Identify gaps (target: 80% overall, 90% for critical paths)
- Write missing unit tests for services

**Tuesday:**
- Write integration tests for database layer
- Test foreign key cascades, transaction rollbacks
- Add E2E tests for GUI workflows

**Wednesday:**
- Update all documentation (README, API_DESIGN, ARCHITECTURE_SPEC)
- Create user guide with screenshots
- Write migration guide (v1.0 → v2.0)

**Thursday:**
- Performance benchmarks (app launch <3s, resume generation <2s)
- Memory profiling (idle <100 MB, analytics dashboard <150 MB)
- Fix performance bottlenecks

**Friday:**
- Final QA testing (checklist: all features, all platforms)
- Build PyInstaller executable (`pyinstaller resume_toolkit.spec`)
- Create GitHub release (v2.0.0) with installer
- **Acceptance Test:** Production-ready release with 80%+ test coverage

**Deliverables:**
- ✅ 80%+ test coverage
- ✅ Updated documentation
- ✅ PyInstaller executable
- ✅ GitHub release v2.0.0

**Acceptance Criteria:**
- [ ] Test coverage ≥80% (pytest --cov-fail-under=80)
- [ ] All documentation current and accurate
- [ ] Executable runs on clean Windows/macOS/Linux
- [ ] No critical bugs in issue tracker
- [ ] Performance benchmarks met (<3s launch, <2s resume gen)

---

## 📊 **RISK REGISTER**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data migration fails | LOW | HIGH | Timestamped backups, rollback scripts, 100% validation |
| Service refactor breaks existing features | MEDIUM | HIGH | Feature parity tests, gradual rollout, backward compatibility |
| GUI refactor introduces regressions | MEDIUM | MEDIUM | Comprehensive E2E tests, visual regression testing |
| Performance degradation | LOW | MEDIUM | Benchmarks at each phase, profiling, optimization sprints |
| API security vulnerabilities | MEDIUM | HIGH | JWT auth, rate limiting, input validation, security audit |
| Test coverage falls short | LOW | LOW | Weekly coverage checks, automated CI/CD, clear coverage targets |

---

## 🎯 **SUCCESS METRICS**

Track progress weekly with these KPIs:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | ≥80% | `pytest --cov` |
| Migration Accuracy | 100% | Row count validation, spot-checks |
| API Response Time | <100ms | Load testing (avg p95) |
| GUI Launch Time | <3s | Stopwatch (cold start) |
| Resume Generation | <2s | Benchmark script |
| Memory Usage | <150 MB | Task Manager / Activity Monitor |
| Code Quality | A grade | SonarQube / CodeClimate |
| Documentation | 100% coverage | Manual review |

---

## 📅 **WEEKLY STANDUP AGENDA**

Every Monday 9am:

1. **Previous Week Review:**
   - Deliverables completed
   - Acceptance criteria met
   - Blockers encountered

2. **Current Week Plan:**
   - Tasks for this week
   - Risk assessment
   - Resource needs

3. **Metrics Update:**
   - Test coverage %
   - Performance benchmarks
   - Bug count (critical/major/minor)

4. **Demos:**
   - Show working features
   - Get feedback
   - Adjust priorities

---

## 🚀 **POST-LAUNCH ROADMAP (Weeks 13-16)**

**Week 13: Monitoring & Bug Fixes**
- Set up Sentry crash reporting
- Monitor user feedback (GitHub issues)
- Hot-fix critical bugs

**Week 14: Performance Optimization**
- Profile slow operations
- Optimize database queries
- Reduce memory footprint

**Week 15: Feature Enhancements**
- Add requested features from user feedback
- Improve UI/UX based on usage patterns
- Expand API with new endpoints

**Week 16: Community Building**
- Write blog posts about architecture decisions
- Create video tutorials
- Encourage contributions (CONTRIBUTING.md)

---

## ✅ **COMPLETION CHECKLIST**

Before declaring "Phase 6 Complete":

### **Code Quality**
- [ ] Test coverage ≥80%
- [ ] No critical bugs open
- [ ] Code reviewed (peer or self)
- [ ] Linting passes (flake8, black)
- [ ] Type hints added (mypy clean)

### **Functionality**
- [ ] All 40+ scripts replaced by services
- [ ] GUI fully modular (4 views)
- [ ] API fully functional (15+ endpoints)
- [ ] Database migration successful
- [ ] Event bus operational

### **Performance**
- [ ] App launch <3s
- [ ] Resume generation <2s
- [ ] API response <100ms (p95)
- [ ] Memory usage <150 MB
- [ ] Database queries <50ms

### **Documentation**
- [ ] README.md updated
- [ ] API documentation (OpenAPI)
- [ ] Architecture diagrams current
- [ ] Migration guide complete
- [ ] User guide with screenshots

### **Deployment**
- [ ] PyInstaller executable builds
- [ ] Installer tested on 3 platforms
- [ ] Auto-update mechanism works
- [ ] GitHub release published
- [ ] Download links verified

### **User Experience**
- [ ] WCAG 2.1 AA compliant
- [ ] Keyboard navigation works
- [ ] Error messages helpful
- [ ] Onboarding smooth
- [ ] Data migration seamless

---

## 🎓 **LESSONS LEARNED LOG**

Document learnings each week:

| Week | Lesson | Action |
|------|--------|--------|
| 1 | SQLite foreign keys not enforced by default | Always `PRAGMA foreign_keys = ON;` |
| 2 | Repository tests slow with real DB | Use in-memory SQLite for unit tests |
| 3 | Pydantic validation too strict | Add `Config.extra = 'ignore'` |
| ... | ... | ... |

---

## 📞 **ESCALATION PATH**

If blocked for >2 days:

1. **Search GitHub Issues** - Similar problems solved?
2. **Check Documentation** - Did you miss something in docs?
3. **Ask Community** - Post on Reddit (r/Python, r/learnpython)
4. **Hire Consultant** - Upwork, Fiverr (if urgent)

---

**Phase Breakdown Complete** ✅

12-week roadmap with weekly deliverables, acceptance criteria, and risk mitigation. Ready for execution.
