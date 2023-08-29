Customizing and extending
=========================

Every pipeline component in ``LangSearch`` exposes settings which allow you to customize the way they work.

The documentation on this will come soon. In the meantime, you can see an example. In our  :doc:`image example <examples/image>`,
we use the setting ``LANGSEARCH_RESIZEIMAGEPIPELINE_RESIZED_WIDTH`` to change the behavior of the ``ResizeImagePipeline``,
which is a component of the :doc:`GenericImagePipeline <pipelines/image>`.

You can also define your own pipeline components and create your own custom pipelines using these components. The documentation
on this feature will come soon.