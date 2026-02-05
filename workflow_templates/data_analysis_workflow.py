"""
Pre-built workflow templates for common use cases
"""

from agentbridge import get_workflow_components


# Get workflow components
WorkflowBuilder = get_workflow_components()[1]


def create_data_analysis_workflow():
    """
    Creates a pre-built workflow for data analysis across multiple frameworks:
    1. CrewAI for data preprocessing and planning
    2. LangGraph for analysis state management
    3. AutoGen for collaborative analysis and reporting
    """
    builder = WorkflowBuilder()
    
    workflow_def = (
        builder
        .add_task(
            framework="crewai_planner",
            operation="plan_analysis",
            inputs={
                "dataset_description": "${dataset_desc}",
                "analysis_goals": "${goals}",
                "required_outputs": ["preprocessing_steps", "analysis_plan"]
            },
            outputs=["preprocessing_steps", "analysis_plan"],
            timeout=600
        )
        .add_task(
            framework="crewai_preprocessor",
            operation="preprocess_data",
            inputs={
                "raw_data": "${raw_dataset}",
                "preprocessing_steps": "${task_0.preprocessing_steps}",
                "target_format": "structured"
            },
            outputs=["cleaned_data", "metadata"],
            dependencies=["task_0"],  # Depends on planning task
            timeout=1200
        )
        .add_task(
            framework="langgraph_analyzer",
            operation="perform_analysis",
            inputs={
                "data": "${task_1.cleaned_data}",
                "analysis_plan": "${task_0.analysis_plan}",
                "analysis_type": "statistical_correlation"
            },
            outputs=["analysis_results", "statistical_measures", "anomalies"],
            dependencies=["task_1"],  # Depends on preprocessing
            timeout=1800
        )
        .add_task(
            framework="autogen_collaborator",
            operation="generate_insights",
            inputs={
                "analysis_results": "${task_2.analysis_results}",
                "statistical_measures": "${task_2.statistical_measures}",
                "stakeholder_requirements": "${requirements}",
                "format_preference": "executive_summary"
            },
            outputs=["insights_report", "recommendations", "visualizations"],
            dependencies=["task_2"],  # Depends on analysis
            timeout=1500
        )
        .build(
            workflow_id="data_analysis_pipeline",
            name="Cross-Framework Data Analysis Pipeline",
            description="End-to-end data analysis using multiple AI agent frameworks"
        )
    )
    
    return workflow_def


def create_content_creation_workflow():
    """
    Creates a pre-built workflow for content creation:
    1. LangGraph for content strategy and state management
    2. CrewAI for research and content planning
    3. AutoGen for collaborative writing and review
    """
    builder = WorkflowBuilder()
    
    workflow_def = (
        builder
        .add_task(
            framework="langgraph_strategist",
            operation="define_content_strategy",
            inputs={
                "target_audience": "${audience}",
                "content_goals": "${goals}",
                "brand_guidelines": "${brand_guidelines}"
            },
            outputs=["strategy", "content_outline", "tone_guidelines"],
            timeout=600
        )
        .add_task(
            framework="crewai_researcher",
            operation="research_topic",
            inputs={
                "research_query": "${research_topic}",
                "strategy": "${task_0.strategy}",
                "sources_required": "${num_sources}"
            },
            outputs=["research_findings", "source_materials", "key_points"],
            dependencies=["task_0"],
            timeout=1200
        )
        .add_task(
            framework="crewai_writer",
            operation="draft_content",
            inputs={
                "outline": "${task_0.content_outline}",
                "research": "${task_1.research_findings}",
                "tone": "${task_0.tone_guidelines}",
                "length_requirement": "${word_count}"
            },
            outputs=["draft_content", "key_messages", "supporting_evidence"],
            dependencies=["task_0", "task_1"],  # Depends on strategy and research
            timeout=900
        )
        .add_task(
            framework="autogen_editor",
            operation="review_and_refine",
            inputs={
                "content": "${task_2.draft_content}",
                "feedback_criteria": "${review_criteria}",
                "collaboration_settings": "${collab_params}"
            },
            outputs=["final_content", "revision_notes", "quality_score"],
            dependencies=["task_2"],  # Depends on draft
            timeout=1200
        )
        .build(
            workflow_id="content_creation_pipeline",
            name="Cross-Framework Content Creation Pipeline",
            description="End-to-end content creation using multiple AI agent frameworks"
        )
    )
    
    return workflow_def


def create_decision_support_workflow():
    """
    Creates a pre-built workflow for decision support:
    1. CrewAI for information gathering and analysis
    2. LangGraph for decision tree traversal
    3. AutoGen for multi-perspective evaluation
    """
    builder = WorkflowBuilder()
    
    workflow_def = (
        builder
        .add_task(
            framework="crewai_analyst",
            operation="gather_information",
            inputs={
                "decision_context": "${context}",
                "information_requirements": "${info_reqs}",
                "stakeholders": "${stakeholder_list}"
            },
            outputs=["information_pack", "facts", "constraints"],
            timeout=900
        )
        .add_task(
            framework="langgraph_decision_tree",
            operation="evaluate_options",
            inputs={
                "information": "${task_0.information_pack}",
                "decision_criteria": "${criteria}",
                "options": "${option_list}"
            },
            outputs=["evaluation_matrix", "risk_assessment", "preliminary_ranking"],
            dependencies=["task_0"],
            timeout=1200
        )
        .add_task(
            framework="autogen_council",
            operation="deliberate_and_advise",
            inputs={
                "evaluation": "${task_1.evaluation_matrix}",
                "risk_assessment": "${task_1.risk_assessment}",
                "stakeholder_perspectives": "${perspectives}",
                "decision_timeline": "${timeline}"
            },
            outputs=["recommendation", "contingency_plans", "implementation_steps"],
            dependencies=["task_1"],
            timeout=1800
        )
        .build(
            workflow_id="decision_support_pipeline",
            name="Cross-Framework Decision Support Pipeline",
            description="Structured decision support using multiple AI agent frameworks"
        )
    )
    
    return workflow_def


# Dictionary of available templates
WORKFLOW_TEMPLATES = {
    "data_analysis": create_data_analysis_workflow,
    "content_creation": create_content_creation_workflow,
    "decision_support": create_decision_support_workflow
}


def get_template(template_name):
    """
    Get a workflow template by name.
    
    Args:
        template_name (str): Name of the template ('data_analysis', 'content_creation', 'decision_support')
    
    Returns:
        WorkflowDefinition: The requested workflow template
    """
    if template_name not in WORKFLOW_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}. Available: {list(WORKFLOW_TEMPLATES.keys())}")
    
    return WORKFLOW_TEMPLATES[template_name]()