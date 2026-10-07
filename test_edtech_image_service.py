from datetime import date, timedelta

import pytest

from edtech_image_service import deliver_course_image


def test_expired_learner_deadline_blocks_generation():
    with pytest.raises(ValueError, match="deadline has passed"):
        deliver_course_image("history", date.today() - timedelta(days=1), "A timeline of the Silk Road")
