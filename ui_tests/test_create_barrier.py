import logging
from typing import Dict, Optional, List

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests.settings import BASE_URL

logger = logging.getLogger(__name__)


def process_step(page, identifier: str, inputs: Optional[Dict] = None) -> Dict:
    if inputs:
        for i in inputs:
            if i['type'] == 'text':
                page.locator(f'id={i["id"]}').fill(i["value"])
            elif i['type'] == 'radio_button':
                radio = page.locator(f'id={i["id"]}')
                expect(radio).to_be_visible()
                radio.click()
            elif i['type'] == 'option':
                option = page.locator(f'id={i["id"]}')
                expect(option).to_be_visible()
                option.select_option(i['value'])
    button = page.locator(f"id={identifier}")
    expect(button).to_be_visible()
    button.click()


def process_error(page, outputs: Optional[List[Dict]] = None) -> Dict:
    pass


def process_conf(conf: Dict, page: Page):
    input_params = {}
    url = reverse(conf['url']['name'], kwargs=conf['url']['kwargs'])
    page.goto(f"{BASE_URL}{url}")

    for i, step in enumerate(conf.get('steps', [])):
        print(f'Processing step {i}')
        if 'title' in step:
            expect(page).to_have_title(step['title'])
        if 'type' in step:
            if step['type'] == 'button':
                response = process_step(page, step['id'], step.get('inputs'))
            elif step['type'] == 'error':
                response = process_error(page, step['outputs'])
            else:
                response = step.process(input_params)
            input_params = response


def test_create_barrier(page: Page):
    conf = {
        'name': 'report_barrier',
        'url': {'name': 'barriers:dashboard', 'kwargs': {}},
        'steps': [
            {
                'id': 'dash-button-0',
                'type': 'button',
                'title': 'Market Access - Homepage',
            },
            {
                'id': 'start-button-0',
                'type': 'button',
                'title': 'Market Access - Report a barrier',
                'inputs': [],
                'outputs': []
            },
            {
                'id': 'continue-button',
                'type': 'button',
                'title': 'Report A Barrier - About the Barrier',
                'inputs': [
                    {'type': 'text', 'id': 'id_barrier-about-title', 'value': 'Test Title'},
                    {'type': 'text', 'id': 'id_barrier-about-summary', 'value': 'Test Summary'}
                ],
                'outputs': []
            },
            {
                'id': 'continue-button',
                'type': 'button',
                'title': 'Report A Barrier - Wizard Framework - Barrier Status',
                'inputs': [
                    {'type': 'radio_button', 'id': 'status-radio-2'},
                    {'type': 'radio_button', 'id': 'start_date_unknown'},
                    {'type': 'radio_button', 'id': 'Yes'},
                ],
                'outputs': []
            },
            {
                'id': 'continue-button',
                'type': 'button',
                'title': 'Report A Barrier - Wizard Framework - Barrier Location',
                'inputs': [
                    {'type': 'option', 'id': 'location_select', 'value': 'TB00016'},
                ],
                'outputs': []
            },
            # {
            #     'id': 'continue-button',
            #     'type': 'button',
            #     'title': 'Report A Barrier - Wizard Framework - Trade Direction',
            #     'inputs': [
            #         {'type': 'radio_button', 'id': 'id_barrier-trade-direction-trade_direction_0'},
            #     ],
            #     'outputs': []
            # },
            # {
            #     'id': 'continue-button',
            #     'type': 'button',
            #     'title': 'Report A Barrier - Wizard Framework - Sectors Affected',
            #     'inputs': [
            #         {'type': 'option', 'id': 'main_sector_select', 'value': 'af959812-6095-e211-a939-e4115bead28a'},
            #     ],
            #     'outputs': []
            # },
            # {
            #     'id': 'continue-button',
            #     'type': 'button',
            #     'title': 'Report A Barrier - Wizard Framework - Companies Affected',
            #     'inputs': [],
            #     'outputs': []
            # },
        ],
    }
    process_conf(conf=conf, page=page)
