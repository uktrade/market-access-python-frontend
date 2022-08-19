export interface FieldDescription {
    type: string;
    widget_type: string;
    required: boolean;
    label: string;
    help_text: string;
    min_length?: number;
    max_length?: number;
    initial_value?: string;
    name: string;
    choices?: [string, string][];
}

export interface FieldOverrides {
    choices?: FieldChoice[];
    label?: string;
    help_text?: string;
}

export interface FieldChoice {
    label: string;
    value: string;
    optGroup?: string;
}

export interface AdminArea {
    id: string;
    name: string;
    disabled_on?: string;
    country: {
        id: string;
        name: string;
    };
}

export interface Country {
    id: string;
    name: string;
    overseas_region: string;
    iso_alpha2_code: string;
}

export interface TradingBloc {
    code: string;
    country_ids: string[];
    name: string;
    short_name: string;
}
