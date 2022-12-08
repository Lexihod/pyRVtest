"""Basic functionality."""

from typing import (
    Any, Container, Dict, List, Optional, Sequence, Tuple
)


# define common types
Array = Any
RecArray = Any
Data = Dict[str, Array]
Options = Dict[str, Any]
Bounds = Tuple[Array, Array]

# define a pool managed by parallel and used by generate_items
pool = None


def format_table_notes(
        header: Sequence, *data: Sequence, title: Optional[str] = None, notes: Optional[Sequence],
        include_border: bool = True, include_header: bool = True, line_indices: Container[int] = ()) -> str:
    """Format table information as a string, which has fixed widths, vertical lines after any specified indices, and
    optionally a title, border, and header.
    """

    # construct the header rows
    row_index = -1
    header_rows: List[List[str]] = []
    header = [[c] if isinstance(c, str) else c for c in header]
    while True:
        header_row = ["" if len(c) < -row_index else c[row_index] for c in header]
        if not any(header_row):
            break
        header_rows.insert(0, header_row)
        row_index -= 1

    # construct the data rows
    data_rows = [[str(c) for c in r] + [""] * (len(header) - len(r)) for r in data]

    # compute column widths
    widths = []
    for column_index in range(len(header)):
        widths.append(max(len(r[column_index]) for r in header_rows + data_rows))

    # create notes
    notes_rows = [[str(c) for c in r] + [""] * (len(header) - len(r)) for r in notes]

    # build the template
    template = "  " .join("{{:^{}}}{}".format(w, "  |" if i in line_indices else "") for i, w in enumerate(widths))

    # build the table
    lines = []
    if title is not None:
        lines.append(f"{title}:")
    if include_border:
        lines.append("=" * len(template.format(*[""] * len(widths))))
    if include_header:
        lines.extend([template.format(*r) for r in header_rows])
        lines.append(template.format(*("-" * w for w in widths)))
    lines.extend([template.format(*r) for r in data_rows])
    if include_border:
        lines.append("=" * len(template.format(*[""] * len(widths))))
    lines.extend([template.format(*r) for r in notes_rows])
    lines.append("=" * len(template.format(*[""] * len(widths)))) 
    return "\n".join(lines)


def format_table_notes_sub(
        header: Sequence, subheader: Sequence, *data: Sequence, title: Optional[str] = None, notes: Optional[Sequence],
        include_border: bool = True, include_header: bool = True, include_subheader: bool = True,
        line_indices: Container[int] = ()) -> str:
    """Format table information as a string, which has fixed widths, vertical lines after any specified indices, and
    optionally a title, border, and header.
    """

    # construct the header rows
    row_index = -1
    header_rows: List[List[str]] = []
    header = [[c] if isinstance(c, str) else c for c in header]
    while True:
        header_row = ["" if len(c) < -row_index else c[row_index] for c in header]
        if not any(header_row):
            break
        header_rows.insert(0, header_row)
        row_index -= 1

    # construct the sub-header rows
    row_index = -1
    subheader_rows: List[List[str]] = []
    subheader = [[c] if isinstance(c, str) else c for c in subheader]
    while True:
        subheader_row = ["" if len(c) < -row_index else c[row_index] for c in subheader]
        if not any(subheader_row):
            break
        subheader_rows.insert(0, subheader_row)
        row_index -= 1

    # construct the data rows
    data_rows = [[str(c) for c in r] + [""] * (len(header) - len(r)) for r in data]

    # compute column widths
    widths = []
    for column_index in range(len(header)):
        widths.append(max(len(r[column_index]) for r in header_rows + subheader_rows + data_rows))

    # construct the notes
    notes_rows = [[str(c) for c in r] + [""] * (len(header) - len(r)) for r in notes]

    # build the template
    template = "  " .join("{{:^{}}}{}".format(w, "  |" if i in line_indices else "") for i, w in enumerate(widths))
    template_notes = "  " .join("{{:^{}}}{}".format(w, "  " if i in line_indices else "") for i, w in enumerate(widths))

    # build the table
    lines = []
    if title is not None:
        lines.append(f"{title}:")
    if include_border:
        lines.append("=" * len(template.format(*[""] * len(widths))))
    if include_header:
        lines.extend([template.format(*r) for r in header_rows])
        lines.append(template.format(*("-" * w for w in widths)))
    if include_subheader:
        lines.extend([template.format(*r) for r in subheader_rows])
        lines.append(template.format(*("-" * w for w in widths)))    
    lines.extend([template.format(*r) for r in data_rows])
    if include_border:
        lines.append("=" * len(template.format(*[""] * len(widths))))
    lines.extend([template_notes.format(*r) for r in notes_rows])
    lines.append("=" * len(template_notes.format(*[""] * len(widths)))) 
    return "\n".join(lines)
