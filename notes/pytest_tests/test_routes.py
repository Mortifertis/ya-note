from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from notes.models import Note

@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    method = client.post if name == 'users:logout' else client.get
    response = method(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_note_exists(note):
    notes_count = Note.objects.count()
    assert notes_count == 1
    assert note.title == 'Заголовок'

@pytest.mark.django_db
def test_empty_db():
    notes_count = Note.objects.count()
    assert notes_count == 0

@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_author(author_client, name, note):
    url = reverse(name, args=(note.slug,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        ('not_author_client', HTTPStatus.NOT_FOUND),
        ('author_client', HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, slug_for_args, expected_status, request
):
    client = request.getfixturevalue(parametrized_client)
    url = reverse(name, args=slug_for_args)
    response = client.get(url)
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    'name, requires_slug',
    (
        ('notes:detail', True),
        ('notes:edit', True),
        ('notes:delete', True),
        ('notes:add', False),
        ('notes:success', False),
        ('notes:list', False),
    ),
)
def test_redirects(client, name, requires_slug, slug_for_args):
    login_url = reverse('users:login')
    args = slug_for_args if requires_slug else None
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
