from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ask_me.models import Profile, Question, Answer, Tag, RateQuestion, RateAnswer
from random import choice, sample, randint


class Command(BaseCommand):
    help = 'fills the DB. --auto 10000 for default'

    def add_arguments(self, parser):
        parser.add_argument('--auto', nargs='+', type=int)

        parser.add_argument('--db_size', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['auto']:
            self.fill_db(options['auto'][0])

        self.stdout.write(self.style.SUCCESS('Data creation was successful'))

    @staticmethod
    def fill_profile(cnt):
        for i in range(cnt):
            Profile.objects.create(
                user_id=User.objects.create_user(
                    username='user_' + str(i),
                    email='user_mail'+str(i)+'@mail.ru',
                    password="1"
                ),
                avatar="img/blank.jpg",
            )

    @staticmethod
    def fill_tag(cnt):
        for i in range(cnt):
            tag = 'tag_' + str(i)
            while Tag.objects.filter(tag_name=tag).exists():
                tag = 'tag_' + str(i)
            Tag.objects.create(tag_name=tag)

    @staticmethod
    def fill_questions(cnt):
        i = 0
        for profile in Profile.objects.all():
            i += 1
            q = Question.objects.create(
                author=profile,
                title='title_by ' + profile.user_id.username + ' ' + str(i),
                question_text='lorem ipsum me' + str(i)
            )

            tag_ids = list(
                Tag.objects.values_list(
                    'tag_name', flat=True
                )
            )
            tags_list = sample(tag_ids, k=3)
            q.tags.set(Tag.objects.on_creation(tags_list))

    @staticmethod
    def fill_answers(cnt):
        profile_ids = list(
            Profile.objects.values_list(
                'id', flat=True
            )
        )
        question_ids = list(
            Question.objects.values_list(
                'id', flat=True
            )
        )
        for i in range(cnt):
            Answer.objects.create(
                author=Profile.objects.get(pk=choice(profile_ids)),
                question=Question.objects.get(pk=choice(question_ids)),
                answer_text='answer_text ' + str(i),
            )

    @staticmethod
    def fill_likes_questions(cnt):
        count = 0
        for question in Question.objects.all():
            for profile in Profile.objects.random_profiles(randint(0, 10)):
                RateQuestion.objects.create(
                    question=question,
                    author=profile,
                )
                count += 1
                if count == cnt:
                    break
            if count == cnt:
                break

    @staticmethod
    def fill_likes_answers(cnt):
        count = 0
        for answer in Answer.objects.all():
            for profile in Profile.objects.random_profiles(randint(0, 10)):
                try:
                    RateAnswer.objects.create(
                        answer=answer,
                        author=profile,
                    )
                except:
                    print("error_reached")
                    count -= 1
                count += 1
                if count == cnt:
                    break
            if count == cnt:
                break

    def fill_db(self, cnt):
        self.fill_profile(cnt)
        self.fill_tag(cnt)
        self.fill_questions(10 * cnt)
        self.fill_answers(80 * cnt)
        self.fill_likes_questions(50 * cnt)
        self.fill_likes_answers(160 * cnt)
