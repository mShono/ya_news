from pytest_django.asserts import assertRedirects

from django.urls import reverse

from news.models import News, Comment


# Указываем фикстуру form_data в параметрах теста.
def test_user_can_create_note(
        author_client, author, form_data, id_for_args_news
    ):
    url = reverse('news:detail', args=id_for_args_news)
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(url, data=form_data)
    # Проверяем, что был выполнен редирект на страницу успешного добавления заметки:
    assertRedirects(response, f'{url}#comments')
    # Считаем общее количество заметок в БД, ожидаем 1 заметку.
    assert Comment.objects.count() == 1
    # Чтобы проверить значения полей заметки -
    # получаем её из базы при помощи метода get():
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.title == form_data['title']
    assert new_comment.text == form_data['text']
    assert new_comment.slug == form_data['slug']
    assert new_comment.author == author
