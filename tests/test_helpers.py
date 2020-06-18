import os
from pathlib import Path
import pytest

from regolith.main import main

helper_map = [
    (["helper", "hello", "--person", "Simon"], "hello Simon\n"),
    (["helper", "a_proprev", "A. Einstein", "nsf", "2020-04-08", "-q",
      "Tess Guebre", "-s", "downloaded", "-t", "A flat world theory"],
     "A. Einstein proposal has been added/updated in proposal reviews\n"),
    (["helper", "a_grppub_readlist", "test the lister",
      "A list to test the lister", "pdf", "--purpose", "Test the lister"],
     "test_the_lister has been added in reading_lists\n"),
    (["helper", "a_projectum", "New projectum", "lyang",
      "--date", "2020-04-29", "-c", "afriend", "-d", "more work",
      "-m", "ascopatz", "-g", "SymPy-1.1", "-u", "2021-01-01"],
     "20ly_newprojectum has been added in projecta\n"),
    (["helper", "l_milestones", "--verbose"],
     "2021-01-01: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-20: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_milestones", "--verbose", "-l", "lyang"],
     "2021-01-01: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: \n    Title: deliverable\n    log url: \n    Purpose: deliver\n    Audience: beginning grad in chemistry\n2020-05-20: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Project lead presentation\n    log url: \n    Purpose: to act as an example milestone.  The date is the date it was finished.  delete the field until it is finished.  In this case, the lead will present what they think is the project after their reading. Add more milestones as needed.\n    Audience: lyang, scopatz, ascopatz\n2020-05-06: lead: lyang, 20ly_newprojectum, status: proposed\n    Type: meeting\n    Title: Kick off meeting\n    log url: \n    Purpose: introduce project to the lead\n    Audience: lyang, scopatz, ascopatz\n"
     ),
    (["helper", "l_projecta", "--verbose"],
     "20ly_newprojectum\n20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--verbose", "-l", "ascopatz"],
     "20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--verbose", "-p", "ascopatz"],
     "20ly_newprojectum\n20sb_firstprojectum\n"
     ),
    (["helper", "l_projecta", "--ended", "-d", "2020-06-02"],
     "20sb_firstprojectum    My first projectum\n    Lead: ascopatz    Members: ascopatz    Collaborators: aeinstein, pdirac\n"
     ),
    (["helper", "l_grants", "-c", "-d", "2020-05-25"],
     "sym2.0, awardnr: , acctn: , 2019-06-01 to 2030-12-31\n, awardnr: , acctn: GG012345, 2015-10-01 to 2025-09-30\n"
     ),
    (["helper", "l_members", "-v"],
     "Anthony Scopatz, professor | group_id: scopatz\n"
     "    orcid: 0000-0002-9432-4248 | github_id: ascopatz\n"
     ),
    (["helper", "l_contacts", "run", "-n", "ny", "-i", "col", "-o", "coffee", "-d", "2020-01-15", "-r", "2"],
     "name: Anthony B Friend, institution: columbiau, email: friend@deed.com\n"
     ),
    (["helper", "l_contacts", "run", "-n", "ny", "-i", "col", "-o", "coffee", "-d", "2019-01-15", "-r", "2"],
     ""
     ),
    (["helper", "u_logurl", "20sb", "-n 1", "this is a test"],
     "20sb_firstprojectum has been updated with a log_url of this is a test\n"
     ),
    (["helper", "u_logurl", "20ly", "this is a test pt.2"],
     "There does not seem to be a projectum with this exact name in this database.\n"
     "However, there are projecta with similar names: \n"
     "1. 20ly_newprojectum\n"
     "Please rerun the u_logurl helper with the same name as previously inputted, "
     "but with the addition of -n followed by a number corresponding to one of the "
     "above listed projectum ids that you would like to update.\n"
     ),
]


@pytest.mark.parametrize("hm", helper_map)
def test_helper_python(hm, make_db, capsys):
    repo = Path(make_db)
    testfile = Path(__file__)
    os.chdir(repo)

    main(args=hm[0])
    out, err = capsys.readouterr()
    assert out == hm[1]

    builddir = repo / "_build" / hm[0][1]
    expecteddir = testfile.parent / "outputs" / hm[0][1]
    are_outfiles = any(builddir.iterdir())
    if are_outfiles and not expecteddir.is_dir():
        print("WARNING: there are built outputs that are not being tested")
    if are_outfiles and expecteddir.is_dir():
        assert_outputs(builddir, expecteddir)

    builddir = repo / "db"
    if expecteddir.is_dir():
        assert_outputs(builddir, expecteddir)


def assert_outputs(builddir, expecteddir):
    """

    Parameters
    ----------
    builddir pathlib.Path object
      the directory where the helper has built the output
    expecteddir pathlib.Path object
      the directory where the expected output is found
    """
    os.chdir(builddir)
    for root, dirs, files in os.walk("."):
        for file in files:
            if file in os.listdir(expecteddir / root):
                fn1 = builddir / root / file
                with fn1.open(mode="r") as f:
                    actual = f.read()
                fn2 = expecteddir / root / file
                with fn2.open(mode="r") as f:
                    expected = f.read()

                # Skip because of a date time in
                if file != "rss.xml":
                    # Fixme proper fix for testing hard coded filepaths on
                    # windows
                    if os.name == "nt":
                        if "tmp" not in expected:
                            if "../.." not in expected:
                                assert expected == actual
                    else:
                        assert expected == actual
