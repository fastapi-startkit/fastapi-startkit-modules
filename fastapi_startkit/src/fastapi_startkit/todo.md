    created_at: Carbon = Field(json_schema_extra={"format": "YYYY-MM-DD HH:mm:ss", "column": "inserted_at"})
    updated_at: Carbon = Field(json_schema_extra={"format": "YYYY-MM-DD HH:mm:ss", "column": "changed_at"})

    # Approach 2: need to tell when updating these values, changed at should trigger in
    inserted_at: Carbon = Field(default_factory=Carbon,json_schema_extra={"format": "YYYY-MM-DD HH:mm:ss"})
    changed_at: Carbon = Field(default_factory=Carbon,json_schema_extra={"format": "YYYY-MM-DD HH:mm:ss"})

    # Approch 3:
    inserted_at: Carbon = CreatedAtField() # this will trigger the ...
    updated_at: Carbon = UpdatedAtField() # This will trigger when it's updated
