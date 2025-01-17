import graphlib


def assemble(*built_in_pipelines):
    """
    These two dicts are constructed

    Each pipeline defines the item key it requires to operate e.g. "html"
    Each pipeline also defines new item keys they create to store results e.g. TikaPipeline.FIXED_HTML
    A pipeline may require different keys depending on ItemType
    pipeline_inputs constructs this mapping from the *built_in_pipelines
    Example:
    pipeline_inputs = {
        PythonReadabilityPipeline: {
            "html": {
                ItemType.HTML: FixHTMLPipeline.FIXED_HTML,
                ItemType.OTHER: TikaPipeline.XML_OUTPUT,
                # ... more item types
            } # Sometimes, instead of using a dict, we use a callable. Use callable(item) to get the required key name.
        },
        # ... more pipelines
    }

    graph describes a pipeline and a set of predecessor pipelines by analyzing *built_in_pipelines
    Predecessors are determined by looking up priority in the built_in_pipeline's ITEM_PIPELINES
    Example:
    graph = {
        PythonReadabilityPipeline: {FixHTMLPipeline, TikaPipeline},
        # ... more pipelines
    }

    We finally do a topological sort to create a list of pipelines where all predecessors are guaranteed to appear
    before the pipeline
    All ItemTypes will pass through all pipelines in the list
    However, if the pipeline_inputs doesn't define a particular ItemType for a pipeline required input,
    then the pipeline won't do anything for that ItemType
    """
    graph = {}
    pipeline_inputs = {}
    for built_in_pipeline in built_in_pipelines:
        sorted_pipelines = [pipeline for (pipeline, priority) in
                            sorted(built_in_pipeline.ITEM_PIPELINES.items(), key=lambda x: x[1])
                            ]
        for i, pipeline in enumerate(sorted_pipelines):
            predecessors = sorted_pipelines[:i]
            if len(predecessors) == 0:
                if pipeline not in graph:
                    graph[pipeline] = set()
            else:
                try:
                    graph[pipeline].update(predecessors)
                except KeyError:
                    graph[pipeline] = set(predecessors)
            for key, value in built_in_pipeline.PIPELINE_INPUTS[pipeline].items():
                try:
                    pipeline_inputs[pipeline][key][built_in_pipeline.ITEM_TYPE] = value
                except KeyError:
                    try:
                        pipeline_inputs[pipeline][key] = {built_in_pipeline.ITEM_TYPE: value}
                    except KeyError:
                        pipeline_inputs[pipeline] = {key: {built_in_pipeline.ITEM_TYPE: value}}
    ts = graphlib.TopologicalSorter(graph)
    try:
        final_order = list(ts.static_order())
    except graphlib.CycleError:
        raise RuntimeError("The built-in pipelines have a circular dependency")
    start = 400
    final_pipeline = {}
    for pipeline in final_order:
        pipeline.INPUTS = pipeline_inputs[pipeline]
        final_pipeline[pipeline] = start
        start += 1
        # Langsearch's pipelines use a priority space of 400 - 600. If we exceed that, we throw an error.
        if start == 601:
            raise RuntimeError("The built-in pipelines have too many items")
    return final_pipeline
