"""
Displays the analytics results within streamlit.
"""

import altair as alt
import pandas as pd
import streamlit as st

from . import utils


def show_results(counts, reset_callback, unsafe_password=None):
    """Show analytics results in streamlit, asking for password if given."""

    # Show header.
    st.title("Analytics Dashboard")


    # Ask for password if one was given.
    show = True
    if unsafe_password is not None:
        password_input = st.text_input(
            "Enter password to show results", type="password"
        )
        if password_input != unsafe_password:
            show = False
            if len(password_input) > 0:
                st.write("Nope, that's not correct ☝️")

    if show:
        # Show traffic.
        st.header("Traffic")
        st.write(f"since {counts['start_time']}")
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Pageviews",
            counts["total_pageviews"],
            help="Every time a user (re-)loads the site.",
        )
        col2.metric(
            "Script runs",
            counts["total_script_runs"],
            help="Every time Streamlit reruns upon changes or interactions.",
        )
        col3.metric(
            "Time spent",
            utils.format_seconds(counts["total_time_seconds"]),
            help=(
                "Time from initial page load to last widget interaction, summed over all users."
            ),
        )
        st.write("")

        df = pd.DataFrame(counts["per_day"])
        base = alt.Chart(df).encode(
            x=alt.X("monthdate(days):O", axis=alt.Axis(title="", grid=True))
        )
        line1 = base.mark_line(point=True, stroke="#5276A7").encode(
            alt.Y(
                "pageviews:Q",
                axis=alt.Axis(
                    titleColor="#5276A7",
                    tickColor="#5276A7",
                    labelColor="#5276A7",
                    format=".0f",
                    tickMinStep=1,
                ),
                scale=alt.Scale(domain=(0, df["pageviews"].max() + 1)),
            )
        )
        line2 = base.mark_line(point=True, stroke="#57A44C").encode(
            alt.Y(
                "script_runs:Q",
                axis=alt.Axis(
                    title="script runs",
                    titleColor="#57A44C",
                    tickColor="#57A44C",
                    labelColor="#57A44C",
                    format=".0f",
                    tickMinStep=1,
                ),
            )
        )
        layer = (
            alt.layer(line1, line2)
            .resolve_scale(y="independent")
            .configure_axis(titleFontSize=15, labelFontSize=12, titlePadding=10)
        )
        st.altair_chart(layer, use_container_width=True)

        # Show widget interactions.
        st.header("Widget interactions")
    

        # This section controls how the tables on individual widgets are shown
        # Before, it was just a json of k/v pairs
        # There is still room for improvement and PRs are welcome
        for i in counts["widgets"].keys():
            st.markdown(f"##### `{i}` Widget Usage")
            if type(counts["widgets"][i]) is dict:
                st.dataframe(
                    pd.DataFrame(
                        {
                            "widget_name": i,
                            "selected_value": list(counts["widgets"][i].keys()),
                            "number_of_interactions": counts["widgets"][i].values(),
                        }
                    ).sort_values(by="number_of_interactions", ascending=False)
                )
            else:
                st.dataframe(
                    pd.DataFrame(
                        {
                            "widget_name": i,
                            "number_of_interactions": counts["widgets"][i],
                        },
                        index=[0],
                    ).sort_values(by="number_of_interactions", ascending=False)
                )

    
