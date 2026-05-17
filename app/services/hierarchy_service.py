from __future__ import annotations

from uuid import UUID

from slugify import slugify
from sqlmodel import Session, select

from app.core.config import SettingsModel
from app.core.paths import course_dir, directory_has_files, discipline_tree_root, ensure_discipline_paths, mkdir_course, rm_tree_safe
from app.exceptions import DomainConflictError, NotFoundError
from app.models.hierarchy import Course, Discipline
from app.repositories import hierarchy as repos


class HierarchyService:
    """Coordinates relational hierarchy + deterministic filesystem scaffolding."""

    def __init__(self, session: Session, settings: SettingsModel) -> None:
        self._session = session
        self._settings = settings

    def get_course_or_raise(self, course_id: UUID) -> Course:
        row = repos.get_course(self._session, course_id)
        if row is None:
            raise NotFoundError("Course not found")
        return row

    def _course_slug_set(self, excluding: UUID | None = None) -> set[str]:
        rows = self._session.exec(select(Course.slug)).all()
        slugs = set(rows)
        if excluding:
            row = repos.get_course(self._session, excluding)
            if row and row.slug in slugs:
                slugs.discard(row.slug)
        return slugs

    def _next_unique_slug(self, base: str, taken: set[str]) -> str:
        candidate = base or slugify("curso")
        if candidate not in taken:
            return candidate
        for i in range(1, 200):
            c2 = f"{candidate}-{i}"
            if c2 not in taken:
                return c2
        raise DomainConflictError("Unable to allocate unique slug.")

    def _discipline_slug_set(self, course_id: UUID, excluding_discipline: UUID | None = None) -> set[str]:
        stmt = select(Discipline.slug).where(Discipline.curso_id == course_id)
        rows = self._session.exec(stmt).all()
        slugs = set(rows)
        if excluding_discipline:
            d = repos.get_discipline(self._session, excluding_discipline)
            if d and d.slug in slugs:
                slugs.discard(d.slug)
        return slugs

    def create_course(self, nome: str) -> Course:
        base = slugify(nome.strip(), max_length=80)
        slug = self._next_unique_slug(base, self._course_slug_set())
        c = Course(nome=nome.strip(), slug=slug)
        self._session.add(c)
        self._session.flush()
        mkdir_course(slug, self._settings.storage_root_abs)
        self._session.commit()
        self._session.refresh(c)
        return c

    def rename_course(self, course_id: UUID, new_nome: str) -> Course:
        course = repos.get_course(self._session, course_id)
        if course is None:
            raise NotFoundError("Course not found")

        taken = self._course_slug_set(excluding=course.id)
        base = slugify(new_nome.strip(), max_length=80)
        new_slug = self._next_unique_slug(base, taken)

        if new_slug != course.slug:
            old_path = course_dir(course.slug, self._settings.storage_root_abs)
            if old_path.exists() and directory_has_files(old_path):
                raise DomainConflictError("Cannot rename course with stored artefacts under course tree.")

        course.nome = new_nome.strip()
        course.slug = new_slug
        self._session.add(course)
        self._session.flush()
        mkdir_course(course.slug, self._settings.storage_root_abs)
        self._session.commit()
        self._session.refresh(course)
        return course

    def delete_course(self, course_id: UUID) -> None:
        course = repos.get_course(self._session, course_id)
        if course is None:
            raise NotFoundError("Course not found")

        for disc in repos.list_disciplines_for_course(self._session, course.id):
            root_d = discipline_tree_root(course.slug, disc.slug, self._settings.storage_root_abs)
            rm_tree_safe(root_d)
            self._session.delete(disc)

        rm_tree_safe(course_dir(course.slug, self._settings.storage_root_abs))
        self._session.delete(course)
        self._session.commit()

    def create_discipline(self, course_id: UUID, nome: str) -> Discipline:
        course = repos.get_course(self._session, course_id)
        if course is None:
            raise NotFoundError("Course not found")

        taken = self._discipline_slug_set(course_id)
        base = slugify(nome.strip(), max_length=80)
        slug = self._next_unique_slug(base, taken)

        mkdir_course(course.slug, self._settings.storage_root_abs)
        d = Discipline(curso_id=course_id, nome=nome.strip(), slug=slug)
        self._session.add(d)
        self._session.flush()
        self._session.refresh(d)
        ensure_discipline_paths(course.slug, slug, self._settings.storage_root_abs)
        self._session.commit()
        self._session.refresh(d)
        return d

    def delete_discipline(self, discipline_id: UUID) -> None:
        disc = repos.get_discipline(self._session, discipline_id)
        if disc is None:
            raise NotFoundError("Discipline not found")
        course = repos.get_course(self._session, disc.curso_id)
        if course is None:
            raise NotFoundError("Course not found")
        rm_tree_safe(discipline_tree_root(course.slug, disc.slug, self._settings.storage_root_abs))
        self._session.delete(disc)
        self._session.commit()

    def rename_discipline(self, discipline_id: UUID, new_nome: str) -> Discipline:
        disc = repos.get_discipline(self._session, discipline_id)
        if disc is None:
            raise NotFoundError("Discipline not found")
        course = repos.get_course(self._session, disc.curso_id)
        if course is None:
            raise NotFoundError("Course not found")

        taken = self._discipline_slug_set(disc.curso_id, excluding_discipline=disc.id)
        base = slugify(new_nome.strip(), max_length=80)
        new_slug = self._next_unique_slug(base, taken)

        if new_slug != disc.slug:
            old_root = discipline_tree_root(course.slug, disc.slug, self._settings.storage_root_abs)
            if old_root.exists() and directory_has_files(old_root):
                raise DomainConflictError("Cannot rename discipline with stored artefacts.")

        disc.nome = new_nome.strip()
        disc.slug = new_slug
        self._session.add(disc)
        self._session.flush()
        ensure_discipline_paths(course.slug, disc.slug, self._settings.storage_root_abs)
        self._session.commit()
        self._session.refresh(disc)
        return disc

    def list_courses_models(self) -> list[Course]:
        return list(repos.list_courses(self._session))

    def list_disciplines_models(self, course_id: UUID) -> list[Discipline]:
        return list(repos.list_disciplines_for_course(self._session, course_id))
