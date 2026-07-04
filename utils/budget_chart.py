import plotly.express as px


def create_budget_chart(total_budget):

    # Remove symbols like ₹, commas, spaces
    amount = str(total_budget)

    amount = amount.replace("₹", "")
    amount = amount.replace(",", "")
    amount = amount.replace(" ", "")

    try:
        amount = int(amount)
    except:
        amount = 50000

    hotel = amount * 0.40
    food = amount * 0.25
    transport = amount * 0.15
    activities = amount * 0.20

    labels = [
        "Hotel",
        "Food",
        "Transport",
        "Activities"
    ]

    values = [
        hotel,
        food,
        transport,
        activities
    ]

    fig = px.pie(
        names=labels,
        values=values,
        title="Budget Distribution"
    )

    return fig