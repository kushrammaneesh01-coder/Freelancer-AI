from backend.db.session import SessionLocal
from backend.db.crud import create_job

def quality_checker(state):
    db = SessionLocal()

    approved = []
    for job in state["jobs"]:
        if len(job["proposal"]) > 100:
            job["approved"] = True

            # ✅ SAVE JOB HERE
            create_job(
                db=db,
                platform=job["platform"],
                title=job["title"],
                score=job["score"],
                proposal=job["proposal"],
                approved=True
            )

            approved.append(job)

    db.close()
    return {"approved_jobs": approved}
