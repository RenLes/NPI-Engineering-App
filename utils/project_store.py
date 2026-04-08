from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _date(offset_days=0):
    return (datetime.now() + timedelta(days=offset_days)).strftime("%Y-%m-%d")


DISCIPLINE_KEYS = [
    "feasibility",
    "structural",
    "geotechnical",
    "hydraulics",
    "roads",
    "tenders",
    "budget",
]


def _empty_disciplines():
    return {k: {"inputs": {}, "files": [], "draft": "", "status": "Not Started", "approved": False} for k in DISCIPLINE_KEYS}


def _seed_projects():
    """Return two realistic mock projects for demo purposes."""
    p1_id = str(uuid.uuid4())
    p2_id = str(uuid.uuid4())
    return {
        p1_id: {
            "id": p1_id,
            "name": "Riverside Commercial Park",
            "client": "Metro Development Corp",
            "location": "45 River Road, Brisbane QLD 4000",
            "description": "Mixed-use commercial development with underground parking, stormwater management, and road upgrades.",
            "phase": "Active",
            "progress": 42,
            "deadline": _date(60),
            "team": ["Sarah Chen (Lead)", "James Patel", "Lin Nguyen"],
            "selected_disciplines": ["feasibility", "structural", "geotechnical", "hydraulics", "tenders"],
            "disciplines": {
                "feasibility": {
                    "inputs": {"site_area": "12,500 m2", "zoning": "Commercial B2", "constraints": "Flood overlay, heritage adjacent"},
                    "files": ["Site_Survey_2026.pdf"],
                    "draft": "Preliminary feasibility assessment indicates the site is suitable for the proposed mixed-use development. Key considerations include the flood overlay affecting basement design and heritage adjacency requiring a 10m setback on the eastern boundary.",
                    "status": "Draft Ready",
                    "approved": False,
                },
                "structural": {
                    "inputs": {"structure_type": "Reinforced Concrete Frame", "storeys": "6", "design_code": "AS 3600-2018"},
                    "files": [],
                    "draft": "",
                    "status": "In Progress",
                    "approved": False,
                },
                "geotechnical": {
                    "inputs": {"soil_type": "Alluvial Clay", "bearing_capacity": "150 kPa", "water_table": "2.5m BGL"},
                    "files": ["Borehole_Log_BH01.pdf", "Borehole_Log_BH02.pdf"],
                    "draft": "Geotechnical investigation reveals alluvial clay deposits to 8m depth overlying sandstone. Recommended foundation: bored piles to rock at 8-10m depth.",
                    "status": "Draft Ready",
                    "approved": False,
                },
                "hydraulics": {
                    "inputs": {"rainfall_intensity": "180 mm/hr (1% AEP)", "catchment_area": "2.8 ha", "runoff_coefficient": "0.85"},
                    "files": ["Rainfall_IFD_Data.xlsx"],
                    "draft": "",
                    "status": "Data Uploaded",
                    "approved": False,
                },
                "roads": {
                    "inputs": {},
                    "files": [],
                    "draft": "",
                    "status": "Not Started",
                    "approved": False,
                },
                "tenders": {
                    "inputs": {},
                    "files": [],
                    "draft": "",
                    "status": "Not Started",
                    "approved": False,
                },
                "budget": {
                    "inputs": {"tender_total": "$285,450", "labour_hours": "334"},
                    "files": [],
                    "draft": "",
                    "status": "Estimate Ready",
                    "approved": False,
                },
            },
            "tasks": [
                {"name": "Site Survey Review", "discipline": "Feasibility", "start": _date(-14), "end": _date(-7), "status": "Complete", "assignee": "Sarah Chen"},
                {"name": "Feasibility Report Draft", "discipline": "Feasibility", "start": _date(-7), "end": _date(0), "status": "In Review", "assignee": "Sarah Chen"},
                {"name": "Borehole Investigation", "discipline": "Geotechnical", "start": _date(-10), "end": _date(-3), "status": "Complete", "assignee": "James Patel"},
                {"name": "Geotech Report Draft", "discipline": "Geotechnical", "start": _date(-3), "end": _date(5), "status": "In Progress", "assignee": "James Patel"},
                {"name": "Structural Concept Design", "discipline": "Structural", "start": _date(0), "end": _date(21), "status": "Not Started", "assignee": "Lin Nguyen"},
                {"name": "Hydraulic Modelling", "discipline": "Hydraulics", "start": _date(5), "end": _date(25), "status": "Not Started", "assignee": "Lin Nguyen"},
                {"name": "Tender Document Prep", "discipline": "Tenders", "start": _date(30), "end": _date(50), "status": "Not Started", "assignee": "Sarah Chen"},
            ],
            "updates": [
                {"timestamp": _now(), "message": "Hydraulics: Rainfall IFD data uploaded", "discipline": "hydraulics"},
                {"timestamp": _now(), "message": "Geotechnical: Borehole logs processed, draft report ready", "discipline": "geotechnical"},
                {"timestamp": _now(), "message": "Feasibility: Draft assessment ready for review", "discipline": "feasibility"},
            ],
            "risks": [
                {"risk": "Flood overlay may require raised floor levels", "likelihood": "High", "impact": "Medium", "mitigation": "Early council pre-lodgement meeting"},
                {"risk": "Rock level variance across site", "likelihood": "Medium", "impact": "High", "mitigation": "Additional boreholes at pile locations"},
            ],
            "created_at": _date(-21),
            "updated_at": _now(),
        },
        p2_id: {
            "id": p2_id,
            "name": "Greenfield Residential Estate",
            "client": "Horizon Living Pty Ltd",
            "location": "Lot 200, Old Northern Road, Caboolture QLD 4510",
            "description": "150-lot residential subdivision with internal roads, stormwater network, sewer, and water reticulation.",
            "phase": "Planning",
            "progress": 15,
            "deadline": _date(120),
            "team": ["David Kim (Lead)", "Emma Walsh"],
            "selected_disciplines": ["feasibility", "geotechnical", "hydraulics"],
            "disciplines": {
                "feasibility": {
                    "inputs": {"site_area": "42 ha", "zoning": "Emerging Community", "constraints": "Koala habitat corridor, steep terrain >15%"},
                    "files": ["Topo_Survey.dwg"],
                    "draft": "",
                    "status": "In Progress",
                    "approved": False,
                },
                "structural": {"inputs": {}, "files": [], "draft": "", "status": "Not Started", "approved": False},
                "geotechnical": {"inputs": {}, "files": [], "draft": "", "status": "Not Started", "approved": False},
                "hydraulics": {"inputs": {}, "files": [], "draft": "", "status": "Not Started", "approved": False},
                "roads": {"inputs": {}, "files": [], "draft": "", "status": "Not Started", "approved": False},
                "tenders": {"inputs": {}, "files": [], "draft": "", "status": "Not Started", "approved": False},
                "budget": {"inputs": {}, "files": [], "draft": "", "status": "Not Started", "approved": False},
            },
            "tasks": [
                {"name": "Topographic Survey Review", "discipline": "Feasibility", "start": _date(-5), "end": _date(5), "status": "In Progress", "assignee": "David Kim"},
                {"name": "Environmental Constraints Mapping", "discipline": "Feasibility", "start": _date(5), "end": _date(20), "status": "Not Started", "assignee": "Emma Walsh"},
                {"name": "Preliminary Lot Layout", "discipline": "Feasibility", "start": _date(15), "end": _date(35), "status": "Not Started", "assignee": "David Kim"},
            ],
            "updates": [
                {"timestamp": _now(), "message": "Feasibility: Topographic survey uploaded", "discipline": "feasibility"},
            ],
            "risks": [
                {"risk": "Koala habitat may reduce developable area by 20%", "likelihood": "High", "impact": "High", "mitigation": "Engage ecologist early, explore offset strategy"},
            ],
            "created_at": _date(-7),
            "updated_at": _now(),
        },
    }


class ProjectStore:
    """In-memory project data store backed by session state."""

    def __init__(self, session_state):
        if "projects" not in session_state:
            session_state["projects"] = _seed_projects()
        self._ss = session_state

    @property
    def projects(self) -> dict:
        return self._ss["projects"]

    def list_projects(self) -> list[dict]:
        return list(self.projects.values())

    def get_project(self, project_id: str) -> dict | None:
        proj = self.projects.get(project_id)
        if proj:
            # Backfill any disciplines added after project creation
            for key in DISCIPLINE_KEYS:
                if key not in proj["disciplines"]:
                    proj["disciplines"][key] = {"inputs": {}, "files": [], "draft": "", "status": "Not Started", "approved": False}
        return proj

    def create_project(self, name, client, location, description, team, selected_disciplines) -> dict:
        pid = str(uuid.uuid4())
        project = {
            "id": pid,
            "name": name,
            "client": client,
            "location": location,
            "description": description,
            "phase": "Planning",
            "progress": 0,
            "deadline": _date(90),
            "team": team if team else [],
            "selected_disciplines": selected_disciplines,
            "disciplines": _empty_disciplines(),
            "tasks": [],
            "updates": [{"timestamp": _now(), "message": "Project created", "discipline": "general"}],
            "risks": [],
            "created_at": _now(),
            "updated_at": _now(),
        }
        self.projects[pid] = project
        return project

    def update_discipline(self, project_id: str, discipline: str, inputs: Optional[dict] = None, files: Optional[list] = None, draft: Optional[str] = None, status: Optional[str] = None, approved: Optional[bool] = None):
        proj = self.get_project(project_id)
        if not proj:
            return
        disc = proj["disciplines"][discipline]
        if inputs is not None:
            disc["inputs"].update(inputs)
        if files is not None:
            disc["files"] = files
        if draft is not None:
            disc["draft"] = draft
        if status is not None:
            disc["status"] = status
        if approved is not None:
            disc["approved"] = approved
        proj["updated_at"] = _now()
        # Add update entry
        label = discipline.replace("_", " ").title()
        proj["updates"].insert(0, {"timestamp": _now(), "message": f"{label}: Data updated — {status or disc['status']}", "discipline": discipline})

    def add_task(self, project_id: str, task: dict):
        proj = self.get_project(project_id)
        if proj:
            proj["tasks"].append(task)
            proj["updated_at"] = _now()

    def add_update(self, project_id: str, message: str, discipline: str = "general"):
        proj = self.get_project(project_id)
        if proj:
            proj["updates"].insert(0, {"timestamp": _now(), "message": message, "discipline": discipline})
            proj["updated_at"] = _now()
