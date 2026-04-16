import pytest_asyncio

from fastapi_startkit.masoniteorm.collection import Collection
from fastapi_startkit.masoniteorm.connections.sqlite_connection import SQLiteConnection
from fastapi_startkit.masoniteorm.models import Model
from fastapi_startkit.masoniteorm.relationships import HasManyThrough
from fastapi_startkit.masoniteorm.schema import Schema
from fastapi_startkit.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES


class Enrolment(Model):
    __table__ = "enrolment"
    __connection__ = "dev"

    active_student_id = int
    in_course_id: int


class Student(Model):
    __table__ = "student"
    __connection__ = "dev"

    student_id: int
    name: str


class Course(Model):
    __table__ = "course"
    __connection__ = "dev"

    course_id: int
    name: str

    students: list[Student] = HasManyThrough(
        ['Student', 'Enrolment'],
        "in_course_id",
        "active_student_id",
        "course_id",
        "student_id"
    )


class TestHasManyThroughRelationship:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        # Reset shared engine cache so each test class gets a fresh in-memory DB.
        SQLiteConnection._shared_engines.clear()

        self.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
            config_path='fastapi_startkit/masoniteorm/tests/integrations/config/database'
        ).on("dev")

        async with (await self.schema.create_table_if_not_exists("student")) as table:
            table.integer("student_id").primary()
            table.string("name")

        async with (await self.schema.create_table_if_not_exists("course")) as table:
            table.integer("course_id").primary()
            table.string("name")

        async with (await self.schema.create_table_if_not_exists("enrolment")) as table:
            table.integer("enrolment_id").primary()
            table.integer("active_student_id")
            table.integer("in_course_id")

        if not await Course.count():
            await Course().get_builder().bulk_create(
                [
                    {"course_id": 10, "name": "Math 101"},
                    {"course_id": 20, "name": "History 101"},
                    {"course_id": 30, "name": "Math 302"},
                    {"course_id": 40, "name": "Biology 302"},
                ]
            )

        if not await Student.count():
            await Student().get_builder().bulk_create(
                [
                    {"student_id": 100, "name": "Bob"},
                    {"student_id": 200, "name": "Alice"},
                    {"student_id": 300, "name": "Steve"},
                    {"student_id": 400, "name": "Megan"},
                ]
            )

        if not await Enrolment.count():
            await Enrolment().get_builder().bulk_create(
                [
                    {"active_student_id": 100, "in_course_id": 30},
                    {"active_student_id": 200, "in_course_id": 10},
                    {"active_student_id": 100, "in_course_id": 10},
                    {"active_student_id": 400, "in_course_id": 20},
                ]
            )

        yield

        # Teardown: drop tables and clear engine cache so tests stay isolated.
        await self.schema.drop_table_if_exists("enrolment")
        await self.schema.drop_table_if_exists("student")
        await self.schema.drop_table_if_exists("course")
        SQLiteConnection._shared_engines.clear()

    async def test_has_many_through_can_eager_load(self):
        courses = await Course.where("name", "Math 101").with_("students").get()
        students = courses.first().students

        assert isinstance(students, Collection)
        assert students.count() == 2

        student1 = students.shift()
        assert isinstance(student1, Student)
        assert student1.name == "Alice"

        student2 = students.shift()
        assert isinstance(student2, Student)
        assert student2.name == "Bob"

        # check .first() and .get() produce the same result
        single = await (
            Course.where("name", "History 101")
            .with_("students")
            .first()
        )
        assert isinstance(single.students, Collection)

        single_get = await (
            Course.where("name", "History 101").with_("students").get()
        )

        single_students = single.students
        single_get_students = single_get.first().students

        assert single_students.count() == 1
        assert single_get_students.count() == 1

        single_name = single_students.first().name
        single_get_name = single_get_students.first().name
        assert single_name == single_get_name

    async def test_has_many_through_eager_load_can_be_empty(self):
        courses = await (
            Course.where("name", "Biology 302")
            .with_("students")
            .get()
        )

        students: Collection = courses.first().students
        assert students is None

    async def test_has_many_through_can_get_related(self):
        course = await Course.where("name", "Math 101").first()
        students = await course.students
        assert isinstance(students, Collection)
        assert isinstance(students.first(), Student)
        assert students.count() == 2

    async def test_has_many_through_has_query(self):
        courses = await Course.where_has(
            "students", lambda query: query.where("name", "Bob")
        ).get()
        assert courses.count() == 2
