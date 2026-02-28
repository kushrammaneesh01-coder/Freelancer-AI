def relevance_filter(state):
    filtered = []
    for job in state["jobs"]:
        score = 80  # replace with ML later
        if score > 70:
            job["score"] = score
            filtered.append(job)
    return {"jobs": filtered}
