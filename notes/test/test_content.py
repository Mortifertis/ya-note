from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTES_COUNT_ON_HOME_PAGE = 11


class TestNotesListPage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        for index in range(NOTES_COUNT_ON_HOME_PAGE):
            Note.objects.create(
                title=f'Note {index}',
                text='Text',
                author=cls.author,
            )

    def setUp(self):
        self.client.force_login(self.author)

    def test_notes_count(self):
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), NOTES_COUNT_ON_HOME_PAGE)

    def test_notes_order(self):
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        ids = [note.id for note in object_list]
        sorted_ids = sorted(ids)
        self.assertEqual(ids, sorted_ids)


class TestNoteDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(title='Заметка', text='Текст', author=cls.author)
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_anonymous_client_redirected(self):
        login_url = reverse('users:login')
        response = self.client.get(self.detail_url)
        self.assertRedirects(response, f'{login_url}?next={self.detail_url}')

    def test_authorized_client_has_links(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        self.assertContains(response, edit_url)
        self.assertContains(response, delete_url)
