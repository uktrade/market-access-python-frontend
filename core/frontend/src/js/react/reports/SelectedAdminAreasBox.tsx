import React from "react";
import { AdminArea, FieldDescription } from "../types";

interface SelectedAdminAreasBoxProps {
    selectedAdminAreas: AdminArea[];
    onRemove: (area: AdminArea) => void;
    onAdd?: (area: string) => void;
    field: FieldDescription;
}

export const SelectedAdminAreasBox: React.FC<SelectedAdminAreasBoxProps> = ({
    selectedAdminAreas,
    onRemove,
    onAdd,
    field,
}) => {
    return (
        <div
            className="selection-list restrict-width"
            id="selected-admin-areas-container"
        >
            {/* hidden input field for submission */}
            <input
                type="hidden"
                name={field.name}
                value={selectedAdminAreas.map((area) => area.id).join(",")}
            />
            <h3 className="selection-list__heading">Selected admin areas</h3>
            <ul className="selection-list__list">
                {selectedAdminAreas.map((area, index) => {
                    return (
                        <li className="selection-list__list__item">
                            <span
                                className="selection-list__list__item__number"
                                data-number={index + 1}
                            ></span>
                            <span>{area.name}</span>
                            <div className="selection-list__list__item__remove-form">
                                <button
                                    className="selection-list__list__item__remove-form__submit"
                                    name="remove_admin_area"
                                    onClick={(event) => {
                                        event.preventDefault();
                                        onRemove(area);
                                    }}
                                >
                                    Remove
                                </button>
                            </div>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};
