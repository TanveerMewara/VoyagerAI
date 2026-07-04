from graphviz import Digraph


def create_workflow():

    graph = Digraph("VoyagerAI")

    graph.attr(rankdir="TB")

    graph.attr(
        "node",
        shape="box",
        style="rounded,filled",
        color="#4CAF50",
        fillcolor="#E8F5E9",
        fontsize="12"
    )

    graph.node("User", "👤 User")

    graph.node("Supervisor", "🧠 Supervisor Agent")

    graph.node("Planner", "📅 Planner Agent")

    graph.node("Budget", "💰 Budget Agent")

    graph.node("Hotel", "🏨 Hotel Agent")

    graph.node("Weather", "🌤 Weather Tool")

    graph.node("Output", "🌍 Final Travel Plan")

    graph.edge("User", "Supervisor")

    graph.edge("Supervisor", "Planner")

    graph.edge("Supervisor", "Budget")

    graph.edge("Supervisor", "Hotel")

    graph.edge("Supervisor", "Weather")

    graph.edge("Planner", "Output")

    graph.edge("Budget", "Output")

    graph.edge("Hotel", "Output")

    graph.edge("Weather", "Output")

    return graph