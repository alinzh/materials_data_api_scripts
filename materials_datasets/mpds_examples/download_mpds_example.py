# Example script to download Seebeck coefficient and structures from MPDS
import os
import pandas as pd
from mpds_client import MPDSDataRetrieval, MPDSDataTypes


def download_property(
    client: MPDSDataRetrieval, 
    phys_prop: str = "Seebeck coefficient"
) -> pd.DataFrame:
    """
    Requests some physical property from MPDS
    
    Parameters
    ----------
    client : MPDSDataRetrieval
        Client to connect to MPDS
    phys_prop : str
        Physical property to request from MPDS, e.g. "Seebeck coefficient" or "Electrical conductivity"
        
    Returns
    -------
        DataFrame with columns: 'Phase', 'Formula', 'SG', 'Entry', 'Property', 'Units', 'Value'
    """
    dfrm = pd.DataFrame(client.get_dataframe({"props": phys_prop}))
    return dfrm

def download_structure(
    client: MPDSDataRetrieval,
    phases: list,
) -> pd.DataFrame:
    """
    Requests chemical structure from MPDS according to phases

    Parameters
    ----------
    phases : list
        Phases of structure for request structures for specific phases

    Returns
    -------
        DataFrame with columns: "phase_id", "formula", "occs_noneq", "cell_abc", "sg_n", "basis_noneq",
        "els_noneq", "entry", "temperature"
    """
    answer_df = pd.DataFrame(
        client.get_data(
            {"props": "atomic structure"},
            phases=phases,
            fields={
                "S": [
                    "phase_id",
                    "chemical_formula",
                    "occs_noneq",
                    "cell_abc",
                    "sg_n",
                    "basis_noneq",
                    "els_noneq",
                    "entry",
                    "condition",
                ]
            },
        ),
        columns=[
            "phase_id",
            "formula",
            "occs_noneq",
            "cell_abc",
            "sg_n",
            "basis_noneq",
            "els_noneq",
            "entry",
            "temperature",
        ],
    )
    print(f"Downloaded {len(answer_df)} structures from MPDS")
    print(answer_df)
    return answer_df


if __name__ == "__main__":
    # set up the MPDS client with your API key
    os.environ["MPDS_API"] = "KEY"
    client = MPDSDataRetrieval(dtype=MPDSDataTypes.PEER_REVIEWED, api_key=os.environ["MPDS_API"])
    
    # get Seebeck coefficient data
    dfrm_seebeck = download_property(client, "Seebeck coefficient")
    print(f"Downloaded {len(dfrm_seebeck)} Seebeck properties from MPDS")
    print(dfrm_seebeck)

    phases = set(dfrm_seebeck['Phase'].tolist())

    # get structures for data with Seebeck coefficient
    dfrm_structure = download_structure(client, phases)

    dfrm_seebeck.rename(columns={'Phase': 'phase_id'}, inplace=True)

    # merge Seebeck properties with structures
    dfrm_merged = pd.merge(dfrm_structure, dfrm_seebeck, on='phase_id', how='inner')
    
    # remove duplicates based on 'phase_id'
    # keep only the first occurrence of each 'phase_id'
    mask = ~dfrm_merged['phase_id'].duplicated()
    result_df = dfrm_merged[mask]
    
    print(f"Downloaded {len(result_df)} Seebeck properties with structures from MPDS")
    print(result_df)
    print("Columns in the result:", result_df.columns.tolist())
    