import inspect
from dumpdie import dd
from fastapi_startkit.masoniteorm.exceptions import InvalidArgument
from fastapi_startkit.masoniteorm.query import QueryBuilder
from ..expressions.expressions import UpdateQueryExpression
from ..collection.Collection import Collection


class AsyncQueryBuilder(QueryBuilder):
    async def first(self, fields=None, query=False):
        if not fields:
            fields = []

        self.select(fields).limit(1)

        if query:
            return self

        result = await (await self.new_connection()).query(
            self.to_qmark(),
            self._bindings,
            results=1
        )

        return await self.prepare_result(result)

    async def find(self, record_id: str | int, column=None, query=False):
        if not column:
            if not self._model:
                raise InvalidArgument("A column to search is required")

            column = self._model.get_primary_key()

        if isinstance(record_id, (list, tuple)):
            self.where_in(column, record_id)
        else:
            self.where(column, record_id)

        if query:
            return self

        return await self.first()

    async def get(self, selects=None):
        if selects is None:
            selects = []
        self.select(*selects)
        result = await (await self.new_connection()).query(self.to_qmark(), self._bindings)

        return await self.prepare_result(result, collection=True)

    async def all(self, selects=None, query=False):
        if selects is None:
            selects = []
        self.select(*selects)

        if query:
            return self

        result = (
            await (await self.new_connection()).query(self.to_qmark(), self._bindings) or []
        )

        return await self.prepare_result(result, collection=True)

    async def statement(self, query, bindings=None):
        if bindings is None:
            bindings = []
        result = await (await self.new_connection()).query(query, bindings)
        return await self.prepare_result(result)

    async def create(
        self,
        creates: dict = None,
        query: bool = False,
        id_key: str = "id",
        cast: bool = True,
        ignore_mass_assignment: bool = False,
        **kwargs,
    ):
        self.set_action("insert")
        model = None
        self._creates = creates if creates else kwargs

        if self._model:
            model = self._model
            self._creates.update(self._creates_related)
            if not ignore_mass_assignment:
                self._creates = model.filter_mass_assignment(self._creates)
            if cast:
                self._creates = model.cast_values(self._creates)

        if query:
            return self

        if model:
            model = model.hydrate(self._creates)
            self.observe_events(model, "creating")
            self._creates.update(model.get_dirty_attributes())

        if not self.dry:
            connection = await self.new_connection()
            query_result = await connection.query(
                self.to_qmark(), self._bindings, results=1
            )

            if model:
                id_key = model.get_primary_key()

            processed_results = self.get_processor().process_insert_get_id(
                self, query_result or self._creates, id_key
            )
        else:
            processed_results = self._creates

        if model:
            model = model.fill(processed_results)
            self.observe_events(model, "created")
            return model

        return processed_results

    async def update(
        self,
        updates: dict,
        dry: bool = False,
        force: bool = False,
        cast: bool = True,
        ignore_mass_assignment: bool = False,
    ):
        model = None
        additional = {}

        if self._model:
            model = self._model
            if not ignore_mass_assignment:
                updates = model.filter_mass_assignment(updates)

        if model and model.is_loaded():
            self.where(model.get_primary_key(), model.get_primary_key_value())
            additional.update(
                {model.get_primary_key(): model.get_primary_key_value()}
            )
            self.observe_events(model, "updating")

        if model:
            if not model.__force_update__ and not force:
                updates = {
                    attr: value
                    for attr, value in updates.items()
                    if (
                        value is None
                        or model.__original_attributes__.get(attr, None)
                        != value
                    )
                }

            if not updates:
                return self if dry or self.dry else model

            if cast:
                updates = model.cast_values(updates)

        if not updates:
            return self

        self._updates = (UpdateQueryExpression(updates),)
        self.set_action("update")
        if dry or self.dry:
            return self

        additional.update(updates)
        connection = await self.new_connection()

        await connection.query(self.to_qmark(), self._bindings)
        if model:
            model.fill(updates)
            self.observe_events(model, "updated")
            model.fill_original(updates)
            return connection.get_row_count()
        return additional

    async def delete(self, column=None, value=None, query=False):
        model = None
        self.set_action("delete")

        if self._model:
            model = self._model

        if column and value:
            if isinstance(value, (list, tuple)):
                self.where_in(column, value)
            else:
                self.where(column, value)

        if query:
            return self

        if model and model.is_loaded():
            self.where(model.get_primary_key(), model.get_primary_key_value())
            self.observe_events(model, "deleting")

        connection = await self.new_connection()
        await connection.query(self.to_qmark(), self._bindings)

        if model:
            self.observe_events(model, "deleted")

        return connection.get_row_count()

    async def count(self, column=None, dry=False):
        alias = (
            "m_count_reserved" if (column == "*" or column is None) else column
        )
        if column == "*":
            self.aggregate("COUNT", f"{column} as {alias}")
        elif column is None:
            self.aggregate("COUNT", f"* as {alias}")
        else:
            self.aggregate("COUNT", f"{column}")

        if dry or self.dry:
            return self

        if not column:
            result = await (await self.new_connection()).query(
                self.to_qmark(), self._bindings, results=1
            )

            if isinstance(result, dict):
                return result.get(alias, 0)

            prepared_result = list(result.values())
            if not prepared_result:
                return 0
            return prepared_result[0]
        else:
            return self

    async def paginate(self, per_page, page=1):
        if page == 1:
            offset = 0
        else:
            offset = (int(page) * per_page) - per_page

        new_from_builder = self.new()
        new_from_builder._order_by = ()
        new_from_builder._columns = ()

        result = await self.limit(per_page).offset(offset).get()
        total = await new_from_builder.count()

        from ..pagination import LengthAwarePaginator
        paginator = LengthAwarePaginator(result, per_page, page, total)
        return paginator

    async def simple_paginate(self, per_page, page=1):
        if page == 1:
            offset = 0
        else:
            offset = (int(page) * per_page) - per_page

        result = await self.limit(per_page).offset(offset).get()

        from ..pagination import SimplePaginator
        paginator = SimplePaginator(result, per_page, page)
        return paginator

    async def chunk(self, chunk_amount):
        chunk_connection = await self.new_connection()
        async for result in chunk_connection.select_many(
            self.to_sql(), (), chunk_amount
        ):
            yield await self.prepare_result(result)

    async def exists(self):
        if await self.first():
            return True
        else:
            return False

    async def new_connection(self):
        if self._connection:
            return self._connection

        self._connection = await self._db_manager.new_connection(self.connection_name)

        return self._connection

    async def prepare_result(self, result, collection=False):
        if self._model and result:
            # eager load here
            hydrated_model = self._model.hydrate(result)
            if (
                self._eager_relation.eagers
                or self._eager_relation.nested_eagers
                or self._eager_relation.callback_eagers
            ) and hydrated_model:
                for eager_load in self._eager_relation.get_eagers():
                    if isinstance(eager_load, dict):
                        # Nested
                        for relation, eagers in eager_load.items():
                            callback = None
                            if inspect.isclass(self._model):
                                related = getattr(self._model, relation)
                            elif callable(eagers):
                                related = getattr(self._model, relation)
                                callback = eagers
                            else:
                                related = self._model.get_related(relation)

                            result_set = related.get_related(
                                self,
                                hydrated_model,
                                eagers=eagers,
                                callback=callback,
                            )

                            if inspect.isawaitable(result_set):
                                result_set = await result_set

                            await self._register_relationships_to_model(
                                result_set,
                                hydrated_model,
                                relation,
                                related,
                            )
                    else:
                        # Not Nested
                        for eager in eager_load:
                            if inspect.isclass(self._model):
                                related = getattr(self._model, eager)
                            else:
                                related = self._model.get_related(eager)

                            result_set = await related.get_related(
                                self, hydrated_model
                            )

                            await self._register_relationships_to_model(
                                related_result=result_set,
                                hydrated_model=hydrated_model,
                                relation_key= eager,
                                related=related,
                            )

            if collection:
                return hydrated_model if result else Collection([])
            else:
                return hydrated_model if result else None

        if collection:
            return Collection(result) if result else Collection([])
        else:
            return result or None
