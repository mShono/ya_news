import pytest

from pytest_django.asserts import assertRedirects
from http import HTTPStatus

from django.urls import reverse

from news.models import News, Comment


# Указываем фикстуру form_data в параметрах теста.
def test_user_can_create_comment(
        author_client, author, form_data, id_for_args_news
    ):
    url = reverse('news:detail', args=id_for_args_news)
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(url, data=form_data)
    # Проверяем, что был выполнен редирект на страницу успешного добавления комментария:
    assertRedirects(response, f'{url}#comments')
    # Считаем общее количество заметок в БД, ожидаем 1 комментарий.
    assert Comment.objects.count() == 1
    # Чтобы проверить значения полей комментария -
    # получаем его из базы при помощи метода get():
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, id_for_args_news):
    url = reverse('news:detail', args=id_for_args_news)
    # Через анонимный клиент пытаемся создать комментарий:
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество комментариев в БД, ожидаем 0 комментариев.
    assert Comment.objects.count() == 0


# В параметрах вызвана фикстура comment: значит, в БД создан комментарий.
def test_author_can_edit_comment(
        author_client, form_data, comment, id_for_args_news,
        id_for_args_comment
    ):
    # Получаем адрес страницы редактирования комментария:
    url = reverse('news:edit', args=id_for_args_comment)
    # В POST-запросе на адрес редактирования комментария
    # отправляем form_data - новые значения для полей комментария:
    response = author_client.post(url, form_data)
    # Проверяем редирект:
    url = reverse('news:detail', args=id_for_args_news)
    assertRedirects(response, f'{url}#comments')
    # Обновляем объект комментария: получаем обновлённые данные из БД:
    comment.refresh_from_db()
    # Проверяем, что атрибуты комментария соответствуют обновлённым:
    assert comment.text == form_data['text']


def test_other_user_cant_edit_note(
        not_author_client, form_data, comment, id_for_args_comment
    ):
    # Получаем адрес страницы редактирования комментария:
    url = reverse('news:edit', args=id_for_args_comment)
    response = not_author_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(id=comment.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment.text == comment_from_db.text


def test_author_can_delete_note(author_client, id_for_args_news, id_for_args_comment):
    url = reverse('news:delete', args=id_for_args_comment)
    response = author_client.post(url)
    url = reverse('news:detail', args=id_for_args_news)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(not_author_client, id_for_args_comment):
    url = reverse('news:delete', args=id_for_args_comment)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
