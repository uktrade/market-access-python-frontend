from barriers.constants import ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES
from utils.models import APIModel


class ActionPlan(APIModel):
    def __init__(self, data):
        super().__init__(data)
        self.stakeholders = [
            Stakeholder(stakeholder) for stakeholder in self.stakeholders
        ]
        self.milestones = [Milestone(milestone) for milestone in self.milestones]

    def get_stakeholder(self, stakeholder_id):
        stakeholder_id_str = str(stakeholder_id)
        stakeholders = [
            stakeholder
            for stakeholder in self.stakeholders
            if stakeholder.id == stakeholder_id_str
        ]
        if stakeholders:
            return stakeholders[0]
        return None

    def get_milestone(self, milestone_id):
        milestone_id_str = str(milestone_id)
        milestones = [
            milestone
            for milestone in self.milestones
            if milestone.id == milestone_id_str
        ]
        if milestones:
            return milestones[0]
        return None


class ActionPlanTask(APIModel):
    def __init__(self, data):
        super().__init__(data)
        self.assigned_stakeholders = [
            Stakeholder(stakeholder) for stakeholder in self.assigned_stakeholders
        ]


class Stakeholder(APIModel):
    def get_status_display(self):
        return ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES[self.status].label


class Milestone(APIModel):
    def __init__(self, data):
        super().__init__(data)
        self.tasks = [ActionPlanTask(task) for task in self.tasks]

    def get_task(self, task_id):
        task_id_str = str(task_id)
        tasks = [task for task in self.tasks if task.id == task_id_str]
        if tasks:
            return tasks[0]
        return None
