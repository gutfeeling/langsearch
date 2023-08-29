Installation
============

To install LangSearch, please use ``pip``.

.. code-block:: console

    pip install langsearch


This basic installation will allow you to use the ``GenericTextPipeline`` (which can index documents with ``text/*``
MIME type) and the ``GenericOtherPipeline`` (which can index everything that
`Apache Tika <https://tika.apache.org/2.7.0/formats.html>`_ can handle).

To use other pipelines provided by LangSearch, please install the corresponding optional dependencies.

.. code-block:: console

    pip install langsearch[audio]  # Downloads dependencies for GenericAudioPipeline (for indexing audio data)
    pip install langsearch[image]  # Downloads dependencies for GenericImagePipeline (for indexing image data)
    pip install langsearch[extras]  # Downloads dependencies for LangSearch pipelines that are not a part of any generic pipelines
    pip install langsearch[all]  # Installs all dependencies

The ``GenericAudioPipeline`` also requires `ffmpeg <https://ffmpeg.org/download.html>`_ installed at the system level.