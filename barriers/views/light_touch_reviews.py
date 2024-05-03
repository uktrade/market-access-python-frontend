# from django.http.response import HttpResponseRedirect
# from django.urls.base import reverse
# from django.views.generic.base import View
#
# from barriers.views.mixins import BarrierMixin, PublicBarrierMixin
# from utils.api.client import MarketAccessAPIClient
#
#
# class PublicBarrierLightTouchReviewsEdit(PublicBarrierMixin, BarrierMixin, View):
#    def get_success_url(self):
#        return reverse(
#            "barriers:public_barrier_detail",
#            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
#        )
#
#    def get(self, request, *args, **kwargs):
#        params = request.GET.dict() or {}
#
#        public_barrier = self.get_public_barrier()
#        barrier = self.get_barrier()
#
#        light_touch_reviews = public_barrier.light_touch_reviews
#        government_organisations = barrier.government_organisations
#
#        organisation_approvals = {org["id"]: False for org in government_organisations}
#        content_approval = False
#        hm_commissioner_approval = False
#
#        for key, val in params.items():
#            if key.startswith("organisation_approval__"):
#                organisation_id = int(key.replace("organisation_approval__", ""))
#                organisation_approvals[organisation_id] = val == "on"
#            elif key == "content_approval":
#                content_approval = val == "on"
#            elif key == "hm_trade_comm_approval":
#                hm_commissioner_approval = val == "on"
#
#        organisation_approvals_list = [
#            {"organisation_id": key, "approval": value}
#            for key, value in organisation_approvals.items()
#        ]
#
#        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
#        client.public_barriers.mark_approvals(
#            id=barrier.id,
#            approvals={
#                "organisations": organisation_approvals_list,
#                "content": content_approval,
#                "hm_commissioner": hm_commissioner_approval,
#            },
#        )
#
#        return HttpResponseRedirect(self.get_success_url())
#
#
# class PublicBarrierLightTouchReviewsHMTradeCommissionerApprovalEnabled(
#    PublicBarrierMixin, BarrierMixin, View
# ):
#    def get_success_url(self):
#        return reverse(
#            "barriers:public_barrier_detail",
#            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
#        )
#
#    def get(self, request, *args, **kwargs):
#
#        public_barrier = self.get_public_barrier()
#        barrier = self.get_barrier()
#        light_touch_reviews = public_barrier.light_touch_reviews
#
#        is_hm_trade_commissioner_approval_enabled = request.GET.get("enabled")
#
#        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
#        client.public_barriers.enable_hm_trade_commissioner_approvals(
#            id=barrier.id, enabled=is_hm_trade_commissioner_approval_enabled
#        )
#
#        return HttpResponseRedirect(self.get_success_url())
#
