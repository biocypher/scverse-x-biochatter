from pydantic import Field, create_model, BaseModel
# To include the uuid we need to modify the BaseModel template
class BaseAPIModel(BaseModel):
    """A base class for all API models.

    Adds 'uuid' to default fields.
    """

    uuid: str | None = Field(
        None, description="Unique identifier for the model instance"
    )

    class Config:
        """BaseModel class configuration.

        Ensures the model can be extended without strict type checking on
        inherited fields.
        """
        # Another option to add the uuid without modifying the actual output schema. Can be accessed with model.Config.schema_extra["uuid"]
        schema_extra = {
            "uuid": "some-unique-identifier"
        }
        arbitrary_types_allowed = True


# As a direct template as input for the create_model function, one could directly define the fields dictionary which contains fields
fields_template = {
    "uuid": (str, Field(description="Unique identifier", default="12345")),
    "data": (float, Field(description="This is a description", default=5, required=True)),
    "another_param": (bool, Field(description="This is a description", default=True, required=False))
}

model = create_model("my_function_name", **fields_template, __base__=BaseAPIModel)
print(model.model_json_schema())
# Or do it with a template dictionary
# Template dictionary for one function
template = {"my_function_name": {
    "title": "my_function_name",
    "uuid": "some-unique-identifier",
    "parameters": {
        "data": {
            "type": float,          # The Python type or `Any`
            "description": "This is a description",  # String describing the field
            "default": 5,    # The field’s default value or `...` if required
        },
        "another_param": {
            "type": bool,
            "description": "This is a description",
            "default": True
        }
    }
}
}

# Build a fields object from the template 
# Loop through all keys (function names)
# Loop through all parameters in each function
# Create field objects for all top level fields. The title (method name) is added directly through the create_model function
# Create a Field object for each parameter
# Create a Pydantic model for each function

for function_name, function_data in template.items():
    fields = {}
    fields["uuid"] = (str, Field(description="Unique identifier", default="12345"))
    for param_name, param_data in function_data["parameters"].items():
        fields[param_name] = (param_data["type"], Field(description=param_data["description"], default=param_data["default"]))
    model = create_model(function_name, **fields, __base__=BaseAPIModel)
    print(model.model_json_schema())
# With this usage of the uuid, the uuid has to be popped out of the fields before being passed to the llm



#check if it can be passed to the llm
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticToolsParser

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm_with_tools = llm.bind_tools([model])
chain = llm_with_tools | PydanticToolsParser(tools=[model])
query = [
	("system", "You're an expert data scientist"), 
	("human", "I want to mark mitochondrial genes of my adata object by checking the basic strings in var_names"),
]
result = chain.invoke(query)
result
