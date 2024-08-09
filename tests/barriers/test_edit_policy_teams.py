from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class EditPolicyTeamsTestCase(MarketAccessTestCase):
    def test_edit_policy_teams_landing_page(self):
        """
        Landing page should load the barrier's policy teams into the session
        """
        response = self.client.get(
            reverse(
                "barriers:edit_policy_teams", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["policy_teams"] == [
            policy_team["id"] for policy_team in self.barrier["policy_teams"]
        ]

        session_policy_team_ids = [
            policy_team["id"] for policy_team in self.client.session["policy_teams"]
        ]
        assert session_policy_team_ids == [
            policy_team["id"] for policy_team in self.barrier["policy_teams"]
        ]

    def test_add_policy_team_choices(self):
        """
        Add policy team page should not include current policy teams in choices
        """
        self.update_session(
            {
                "policy_teams": [
                    {
                        "id": policy_team["id"],
                        "title": policy_team["title"],
                    }
                    for policy_team in self.barrier["policy_teams"]
                ],
            }
        )

        response = self.client.get(
            reverse(
                "barriers:add_policy_team", kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        choice_values = [k for k, v in form.fields["policy_team"].choices]

        for policy_team_id in self.barrier["policy_teams"]:
            assert policy_team_id["id"] not in choice_values

    @patch("utils.api.resources.APIResource.patch")
    def test_add_policy_team(self, mock_patch):
        """
        Add policy team page should add a policy team to the session, not call the API
        """
        self.update_session(
            {
                "policy_teams": [
                    {
                        "id": policy_team["id"],
                        "title": policy_team["title"],
                    }
                    for policy_team in self.barrier["policy_teams"]
                ],
            }
        )

        response = self.client.post(
            reverse(
                "barriers:add_policy_team", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"policy_team": "12"},
        )
        assert response.status_code == HTTPStatus.FOUND

        session_policy_team_ids = [
            policy_team["id"] for policy_team in self.client.session["policy_teams"]
        ]

        assert session_policy_team_ids == [10, 11, 12]
        assert mock_patch.called is False

    def test_edit_policy_teams_confirmation_form(self):
        """
        Edit policy teams form should match the policy teams in the session
        """
        policy_teams_ids = [
            policy_team["id"] for policy_team in self.barrier["policy_teams"]
        ]
        new_policy_teams_ids = policy_teams_ids + [12]

        self.update_session(
            {
                "policy_teams": [
                    {
                        "id": policy_team_id,
                        "title": "Title",
                    }
                    for policy_team_id in new_policy_teams_ids
                ],
            }
        )

        response = self.client.get(
            reverse(
                "barriers:edit_policy_teams_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.initial["policy_teams"] == new_policy_teams_ids

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_policy_teams_confirm(self, mock_patch):
        """
        Saving barrier policy teams should call the API
        """
        new_policy_teams_ids = [
            policy_team["id"] for policy_team in self.barrier["policy_teams"]
        ] + [12]

        self.update_session(
            {
                "policy_teams": [
                    {
                        "id": policy_team_id,
                        "title": "Title",
                    }
                    for policy_team_id in new_policy_teams_ids
                ],
            }
        )

        response = self.client.post(
            reverse(
                "barriers:edit_policy_teams_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"policy_teams": new_policy_teams_ids},
        )

        mock_patch.assert_called_with(
            id=self.barrier["id"],
            policy_teams=[
                str(policy_team_id) for policy_team_id in new_policy_teams_ids
            ],
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_remove_policy_team(self, mock_patch):
        """
        Removing a policy team should remove it from the session, not call the API
        """
        new_policy_teams_ids = [
            policy_team["id"] for policy_team in self.barrier["policy_teams"]
        ] + [12]

        self.update_session(
            {
                "policy_teams": [
                    {"id": policy_team_id, "title": "Title"}
                    for policy_team_id in new_policy_teams_ids
                ],
            }
        )

        response = self.client.post(
            reverse(
                "barriers:remove_policy_team", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"policy_team_id": self.barrier["policy_teams"][0]["id"]},
        )
        assert response.status_code == HTTPStatus.FOUND

        session_policy_team_ids = [
            policy_team["id"] for policy_team in self.client.session["policy_teams"]
        ]

        assert session_policy_team_ids == (
            [policy_team["id"] for policy_team in self.barrier["policy_teams"][1:]]
            + [12]
        )
        assert mock_patch.called is False
