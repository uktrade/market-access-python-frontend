from barriers.constants import ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES
from utils.models import APIModel


class ActionPlan(APIModel):
    def get_stakeholder(self, stakeholder_id):
        stakeholder_id_str = str(stakeholder_id)
        stakeholder = [
            stakeholder
            for stakeholder in self.stakeholders
            if stakeholder["id"] == stakeholder_id_str
        ]
        if stakeholder:
            return Stakeholder(stakeholder[0])
        return None


class ActionPlanMilestone(APIModel):
    pass


class ActionPlanTask(APIModel):
    pass


class Stakeholder(APIModel):
    def get_status_display(self):
        return ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES[self.status].label
