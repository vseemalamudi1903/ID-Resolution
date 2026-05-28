import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Define styles
    source_color = '#f5f5f5'
    agent_color = '#e1f5fe'
    hub_color = '#fff9c4'
    text_color = '#333333'

    # 1. Data Sources
    ax.add_patch(patches.Rectangle((0.5, 5), 2.5, 2, facecolor=source_color, edgecolor='#cccccc', lw=2))
    ax.text(1.75, 7.2, "Data Sources", ha='center', fontweight='bold', fontsize=12)
    ax.text(1.75, 6.3, "Enterprise Data\n(SKUs, Inv, Sales)\n\nCompetitor Web\n(Amazon, etc.)", ha='center', fontsize=10)

    # 2. Agentic Intelligence Layer (RIAES)
    ax.add_patch(patches.Rectangle((4, 1), 6, 6, facecolor=agent_color, edgecolor='#0288d1', lw=2))
    ax.text(7, 7.2, "RIAES Intelligence Layer (PydanticAI)", ha='center', fontweight='bold', fontsize=12, color='#01579b')

    agents = [
        "Data Load Agent", "Scraper Agent", "Pricing Agent",
        "Inventory Agent", "Strategy Agent", "Planning Agent"
    ]
    for i, agent in enumerate(agents):
        y_pos = 6 - (i * 0.8)
        ax.add_patch(patches.FancyBboxPatch((4.5, y_pos), 5, 0.6, boxstyle="round,pad=0.1", facecolor='white', edgecolor='#0288d1'))
        ax.text(7, y_pos+0.3, agent, ha='center', va='center', fontsize=10)

    # 3. Governance Hub
    ax.add_patch(patches.Rectangle((11, 3), 2.5, 3, facecolor=hub_color, edgecolor='#fbc02d', lw=2))
    ax.text(12.25, 6.2, "Governance & Control", ha='center', fontweight='bold', fontsize=12, color='#f57f17')
    ax.text(12.25, 4.5, "HITL Portal\n(Approvals)\n\nAudit Log\n(State Storage)", ha='center', fontsize=10)

    # Connections
    ax.annotate("", xy=(4, 6), xytext=(3, 6), arrowprops=dict(arrowstyle="->", lw=1.5, color='#666666'))
    ax.annotate("", xy=(4, 2), xytext=(3, 5), arrowprops=dict(arrowstyle="->", lw=1.5, color='#666666'))
    ax.annotate("", xy=(11, 4.5), xytext=(10, 4.5), arrowprops=dict(arrowstyle="->", lw=1.5, color='#666666'))
    ax.annotate("Execution Loop", xy=(1.75, 5), xytext=(12.25, 3),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#444444', connectionstyle="arc3,rad=-0.3"),
                ha='center', fontsize=9)

    plt.title("RIAES: Autonomous Retail Intelligence Architecture", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('architecture_diagram.png', dpi=150, bbox_inches='tight')
    print("RIAES Architecture diagram generated.")

if __name__ == "__main__":
    create_architecture_diagram()
