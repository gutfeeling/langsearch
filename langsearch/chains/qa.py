import logging

from langchain.chains.base import Chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from pydantic import Extra
import tiktoken

from langsearch.pipelines.common.index import SimpleIndexPipeline

logger = logging.getLogger(__name__)


class QAChain(Chain):
    class Config:
        extra = Extra.allow

    def __init__(self,
                 *args,
                 qa_chain=load_qa_chain(llm=OpenAI(temperature=0, model_name="text-davinci-003")),
                 qa_chain_question_input_name="question",
                 document_search_question_input_name="question",
                 length_function=lambda text: len(tiktoken.get_encoding("gpt2").encode(text)),
                 max_context_size=4097,
                 top=4,
                 method=SimpleIndexPipeline().get_similar_documents,
                 **kwargs
                 ):
        super().__init__(*args, **kwargs)
        self.qa_chain = qa_chain
        self.qa_chain_question_input_name = qa_chain_question_input_name
        self.document_search_question_input_name = document_search_question_input_name
        self.length_function = length_function
        self.max_context_size = max_context_size
        self.top = top
        self.method = method

    @property
    def input_keys(self):
        return list({self.qa_chain_question_input_name, self.document_search_question_input_name})

    @property
    def output_keys(self):
        return self.qa_chain.output_keys + ["docs"]

    def _call(self, inputs):
        if isinstance(self.qa_chain, StuffDocumentsChain):
            prompt_template = self.qa_chain.llm_chain.prompt
            empty_prompt = prompt_template.format(**{input_var: "" for input_var in prompt_template.input_variables})
            prompt_length = self.length_function(empty_prompt)
            question_length = self.length_function(inputs[self.qa_chain_question_input_name])
            remaining = self.max_context_size - prompt_length - question_length - 100  # -100 for safety
            docs = self.method(inputs[self.document_search_question_input_name], token_limit=remaining,
                               length_function=self.length_function
                               )
        else:
            docs = self.method(inputs[self.document_search_question_input_name], top=self.top)
        qa_chain_inputs = inputs.copy()
        if self.document_search_question_input_name != self.qa_chain_question_input_name:
            del qa_chain_inputs[self.document_search_question_input_name]
        return {"docs": docs,
                **self.qa_chain({**qa_chain_inputs, self.qa_chain.input_key: docs}, return_only_outputs=True)
                }
