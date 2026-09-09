"""
Tests for app/services/image_management.py

Covers the backend (FastAPI/Python) unit test cases from
IDRS_Test Plan_V.0.2.0 — Chapter 3.1 "Image Management Module":

  UTC-36 : Create Image Record          -> create_image_management()
  UTC-37 : View Image List (Signed URLs) -> get_all_image_management_signed()
  UTC-38 : Delete Image Record          -> delete_image_management()

Layer: service-layer only — the DB Session is a MagicMock and Supabase
`get_signed_url` is patched.

Spec vs. implementation notes:
  - UTC-36-TC-02 (chart FK not found): `create_image_management` looks up the
    chart and raises HTTPException(404, "Dental chart not found").
  - UTC-36-TC-04 (unsupported file type) and TC-05 (file > 10 MB) are enforced
    by validators on `ImageManagementCreate` (extension of `image_file`, and
    the `file_size` upload-metadata field).
"""
import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

import pydantic

from app.models.enums import ImageCategory
from app.models.image_management import ImageManagement, ImageManagementCreate
from app.services import image_management as svc


# ---------------------------------------------------------------------------
# Constants (match UTC-36 .. UTC-38 in the Test Plan)
# ---------------------------------------------------------------------------
CHART_ID = uuid.UUID("8052cd7e-6ae8-4b11-8288-6dc29f9d517a")
NONEXISTENT_CHART_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")
IMAGE_ID = uuid.UUID("005599f7-cf0a-4db5-9e2e-1fe71f93a339")
NONEXISTENT_IMAGE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def make_image(image_id=None, chart_id=CHART_ID, image_type=ImageCategory.panoramic_xray,
               image_file="abc.jpg", description=None):
    return ImageManagement(
        image_id=image_id or uuid.uuid4(),
        chart_id=chart_id,
        image_type=image_type,
        image_file=image_file,
        description=description,
    )


# ===========================================================================
# UTC-36 : Create Image Record
# ===========================================================================
class TestCreateImageRecord:

    def test_utc_36_tc_01_create_with_valid_payload(self, mock_session):
        """Success: create an image record with a complete valid payload."""
        payload = ImageManagementCreate(
            image_type=ImageCategory.panoramic_xray,
            image_file="abc.jpg",
            description="Pre-op panoramic X-ray",
        )

        result = svc.create_image_management(mock_session, CHART_ID, payload)

        assert result.chart_id == CHART_ID
        assert result.image_type == ImageCategory.panoramic_xray
        assert result.image_file == "abc.jpg"
        assert result.description == "Pre-op panoramic X-ray"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_utc_36_tc_02_reject_when_chart_does_not_exist(self, mock_session):
        """Failure: reject creation when chart_id does not refer to an existing chart."""
        # Simulate the chart lookup returning None.
        mock_session.get.return_value = None
        payload = ImageManagementCreate(
            image_type=ImageCategory.panoramic_xray,
            image_file="abc.jpg",
            description="Pre-op panoramic X-ray",
        )

        with pytest.raises(HTTPException) as exc:
            svc.create_image_management(mock_session, NONEXISTENT_CHART_ID, payload)

        assert exc.value.status_code == 404
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_utc_36_tc_03_reject_invalid_image_type(self):
        """Failure: reject an image_type that is not in the ImageCategory enum."""
        with pytest.raises(pydantic.ValidationError):
            ImageManagementCreate(
                image_type="xray_side",  # not a valid ImageCategory
                image_file="abc.jpg",
                description="Pre-op panoramic X-ray",
            )

    def test_utc_36_tc_04_reject_unsupported_file_type(self):
        """Failure: reject an unsupported upload file type (.pdf)."""
        with pytest.raises(pydantic.ValidationError, match="not a supported image file type"):
            ImageManagementCreate(
                image_type=ImageCategory.other,
                image_file="abc.pdf",
                description="Pre-op panoramic X-ray",
            )
    
    def test_utc_36_tc_05_reject_file_larger_than_10mb(self):
        """Failure: reject an image file larger than 10 MB."""
        with pytest.raises(pydantic.ValidationError, match="exceeds the 10 MB limit"):
            ImageManagementCreate(
                image_type=ImageCategory.panoramic_xray,
                image_file="large_image.jpg",
                file_size=11 * 1024 * 1024,
                description="Pre-op panoramic X-ray",
            )


# ===========================================================================
# UTC-37 : View Image List (Signed URLs)
# ===========================================================================
class TestViewImageListSigned:

    def test_utc_37_tc_01_chart_has_two_images(self, mock_session, monkeypatch):
        """Success: chart has 2 image records, each enriched with a signed URL."""
        images = [make_image(image_file="a.jpg"), make_image(image_file="b.jpg")]
        mock_session.exec.return_value.all.return_value = images

        monkeypatch.setattr(
            svc, "get_signed_url",
            lambda path: f"https://signed.url/{path}",
        )

        result = svc.get_all_image_management_signed(mock_session, CHART_ID, skip=0, limit=100)

        assert len(result) == 2
        for item, src in zip(result, images):
            assert item["image_file"] == src.image_file
            assert item["image_url"] == f"https://signed.url/panoramic_xray/{src.image_file}"

    def test_utc_37_tc_02_chart_has_no_images(self, mock_session, monkeypatch):
        """Success: chart has no image records -> returns []."""
        mock_session.exec.return_value.all.return_value = []
        monkeypatch.setattr(svc, "get_signed_url", lambda path: "https://signed.url/x")

        result = svc.get_all_image_management_signed(mock_session, CHART_ID, skip=0, limit=100)

        assert result == []

    def test_utc_37_tc_03_signed_url_generation_fails(self, mock_session, monkeypatch):
        """Failure: Supabase fails to generate a signed URL -> exception propagates."""
        mock_session.exec.return_value.all.return_value = [make_image()]

        def _boom(path):
            raise Exception("Failed to generate signed URL for " + path)

        monkeypatch.setattr(svc, "get_signed_url", _boom)

        with pytest.raises(Exception, match="Failed to generate signed URL"):
            svc.get_all_image_management_signed(mock_session, CHART_ID, skip=0, limit=100)


# ===========================================================================
# UTC-38 : Delete Image Record
# ===========================================================================
class TestDeleteImageRecord:

    def test_utc_38_tc_01_delete_image_with_linked_analysis(self, mock_session):
        """Success: deleting an image also deletes its linked AI detection analysis."""
        image = make_image(image_id=IMAGE_ID)
        linked_analysis = MagicMock(name="AIDetectionAnalysis")
        mock_session.get.return_value = image
        mock_session.exec.return_value.all.return_value = [linked_analysis]

        svc.delete_image_management(mock_session, IMAGE_ID)

        deleted = [c.args[0] for c in mock_session.delete.call_args_list]
        assert linked_analysis in deleted
        assert image in deleted
        mock_session.commit.assert_called_once()

    def test_utc_38_tc_02_delete_image_without_linked_analysis(self, mock_session):
        """Success: deleting an image with no linked AI detection analysis."""
        image = make_image(image_id=IMAGE_ID)
        mock_session.get.return_value = image
        mock_session.exec.return_value.all.return_value = []

        svc.delete_image_management(mock_session, IMAGE_ID)

        mock_session.delete.assert_called_once_with(image)
        mock_session.commit.assert_called_once()

    def test_utc_38_tc_03_delete_nonexistent_image(self, mock_session):
        """Failure: image_id does not exist -> HTTPException(404)."""
        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc:
            svc.delete_image_management(mock_session, NONEXISTENT_IMAGE_ID)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Image not found"
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()
