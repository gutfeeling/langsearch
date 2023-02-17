import graphlib


def assemble(*built_in_pipelines):
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
        if start == 601:
            raise RuntimeError("The built-in pipelines have too many items")
    return final_pipeline
