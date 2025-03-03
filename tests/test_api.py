import pytest


def test_api_build(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "7eb856bfaccac42d16ba5ecfa6b2ebe5"


def test_api_build_filesystem_ext4(app, upstream):
    client = app.test_client()
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
            filesystem="ext4",
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "ad75ad5848b4b054393f8eedde61e2a8"

    config = (
        app.config["CACHE_PATH"] / "cache/TESTVERSION/testtarget/testsubtarget/.config"
    ).read_text()
    assert "# CONFIG_TARGET_ROOTFS_SQUASHFS is not set" in config
    assert "CONFIG_TARGET_ROOTFS_EXT4FS=y" in config


def test_api_build_filesystem_squashfs(app, upstream):
    client = app.test_client()
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
            filesystem="squashfs",
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "a7228bb7886a63850ff3e9e5c3e8b452"
    config = (
        app.config["CACHE_PATH"] / "cache/TESTVERSION/testtarget/testsubtarget/.config"
    ).read_text()
    assert "# CONFIG_TARGET_ROOTFS_EXT4FS is not set" in config
    assert "CONFIG_TARGET_ROOTFS_SQUASHFS=y" in config


def test_api_build_filesystem_empty(app, upstream):
    client = app.test_client()
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
            filesystem="",
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "7eb856bfaccac42d16ba5ecfa6b2ebe5"
    config = (
        app.config["CACHE_PATH"] / "cache/TESTVERSION/testtarget/testsubtarget/.config"
    ).read_text()
    assert "CONFIG_TARGET_ROOTFS_EXT4FS=y" in config
    assert "CONFIG_TARGET_ROOTFS_SQUASHFS=y" in config


def test_api_build_filesystem_reset(app, upstream):
    client = app.test_client()
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
            filesystem="ext4",
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "ad75ad5848b4b054393f8eedde61e2a8"
    assert (
        "# CONFIG_TARGET_ROOTFS_SQUASHFS is not set"
        in (
            app.config["CACHE_PATH"]
            / "cache/TESTVERSION/testtarget/testsubtarget/.config"
        ).read_text()
    )

    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "7eb856bfaccac42d16ba5ecfa6b2ebe5"
    assert (
        "# CONFIG_TARGET_ROOTFS_SQUASHFS is not set"
        not in (
            app.config["CACHE_PATH"]
            / "cache/TESTVERSION/testtarget/testsubtarget/.config"
        ).read_text()
    )


def test_api_build_filesystem_bad(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
            filesystem="bad",
        ),
    )
    assert response.status == "400 BAD REQUEST"


def test_api_latest_default(client):
    response = client.get("/api/latest")
    assert response.status == "302 FOUND"


def test_api_build_mapping(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testvendor,testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "29c5a7ba0a14105e12ee1d4f96b0832e"


def test_api_build_mapping_abi(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testvendor,testprofile",
            packages=["test1-1", "test2"],
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "333eb925b5ae7382ea5959455afb02d6"


def test_api_build_bad_target(client):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtargetbad",
            profile="testvendor,testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "400 BAD REQUEST"
    assert (
        response.json.get("detail") == "Unsupported target: testtarget/testsubtargetbad"
    )


def test_api_build_get(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.json["request_hash"] == "7eb856bfaccac42d16ba5ecfa6b2ebe5"
    response = client.get("/api/v1/build/7eb856bfaccac42d16ba5ecfa6b2ebe5")
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "7eb856bfaccac42d16ba5ecfa6b2ebe5"


def test_api_build_packages_versions(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages_versions={"test1": "1.0", "test2": "2.0"},
        ),
    )
    assert response.json["request_hash"] == "eb06f1e283c6a7c0c209b1cbb8670a0e"
    response = client.get("/api/v1/build/eb06f1e283c6a7c0c209b1cbb8670a0e")
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "eb06f1e283c6a7c0c209b1cbb8670a0e"


def test_api_build_packages_duplicate(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
            packages_versions={"test1": "1.0", "test2": "2.0"},
        ),
    )
    assert response.status == "200 OK"


def test_api_build_get_not_found(client):
    response = client.get("/api/v1/build/testtesttest")
    assert response.status == "404 NOT FOUND"


def test_api_build_get_no_post(client):
    response = client.post("/api/v1/build/0222f0cd9290")
    assert response.status == "405 METHOD NOT ALLOWED"


def test_api_build_empty_packages_list(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=[],
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "fd6956b610cc8e21b4edfc9c5a307451"


def test_api_build_withouth_packages_list(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "fd6956b610cc8e21b4edfc9c5a307451"


def test_api_build_prerelease_snapshot(client):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="21.02-SNAPSHOT",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "Unsupported profile: testprofile"


def test_api_build_prerelease_rc(client):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="21.02.0",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "Unsupported profile: testprofile"


def test_api_build_bad_packages_str(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages="testpackage",
        ),
    )
    assert response.status == "400 BAD REQUEST"
    assert (
        response.json.get("detail")
        == "'testpackage' is not of type 'array' - 'packages'"
    )


def test_api_build_empty_request(client):
    response = client.post("/api/v1/build")
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "None is not of type 'object'"


@pytest.mark.slow
def test_api_build_real_x86(app):
    client = app.test_client()
    app.config["UPSTREAM_URL"] = "https://downloads.openwrt.org"
    response = client.post(
        "/api/v1/build",
        json=dict(
            target="x86/64",
            version="SNAPSHOT",
            packages=["tmux", "vim"],
            profile="some_random_cpu_which_doesnt_exists_as_profile",
        ),
    )

    assert response.status == "200 OK"
    assert response.json.get("id") == "generic"

    response = client.post(
        "/api/v1/build",
        json=dict(
            target="x86/64",
            version="SNAPSHOT",
            packages=["tmux", "vim"],
            profile="some_random_cpu_which_doesnt_exists_as_profile",
            filesystem="ext4",
        ),
    )

    assert response.status == "200 OK"
    assert response.json.get("id") == "generic"


@pytest.mark.slow
def test_api_build_real_ath79(app):
    client = app.test_client()
    app.config["UPSTREAM_URL"] = "https://downloads.openwrt.org"
    response = client.post(
        "/api/v1/build",
        json=dict(
            target="ath79/generic",
            version="SNAPSHOT",
            packages=["tmux", "vim"],
            profile="tplink_tl-wdr4300-v1",
        ),
    )

    assert response.status == "200 OK"
    assert response.json.get("id") == "tplink_tl-wdr4300-v1"

    response = client.post(
        "/api/v1/build",
        json=dict(
            target="ath79/generic",
            version="SNAPSHOT",
            packages=["tmux", "vim"],
            profile="tplink_tl-wdr4300-v1",
            filesystem="squashfs",
        ),
    )

    assert response.status == "200 OK"
    assert response.json.get("id") == "tplink_tl-wdr4300-v1"


def test_api_build_needed(client):
    response = client.post(
        "/api/v1/build",
        json=dict(profile="testprofile", target="testtarget/testsubtarget"),
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "'version' is a required property"
    assert response.json.get("title") == "Bad Request"
    response = client.post(
        "/api/v1/build",
        json=dict(version="TESTVERSION", target="testtarget/testsubtarget"),
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "'profile' is a required property"
    assert response.json.get("title") == "Bad Request"
    response = client.post(
        "/api/v1/build", json=dict(version="TESTVERSION", profile="testprofile")
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "'target' is a required property"
    assert response.json.get("title") == "Bad Request"


def test_api_build_bad_distro(client):
    response = client.post(
        "/api/v1/build",
        json=dict(
            distro="Foobar",
            target="testtarget/testsubtarget",
            version="TESTVERSION",
            profile="testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "Unsupported distro: Foobar"


def test_api_build_bad_branch(client):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="10.10.10",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "Unsupported branch: 10.10.10"


def test_api_build_bad_version(client):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="19.07.2",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "Unsupported version: 19.07.2"


def test_api_build_bad_profile(client):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="Foobar",
            packages=["test1", "test2"],
        ),
    )
    assert response.status == "400 BAD REQUEST"
    assert response.json.get("detail") == "Unsupported profile: Foobar"


def test_api_build_bad_packages(client):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test4"],
        ),
    )
    assert response.json.get("detail") == "Unsupported package(s): test4"
    assert response.status == "422 UNPROCESSABLE ENTITY"


def test_api_build_package_to_remove_diff_packages_false(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2", "package_to_remove"],
            diff_packages=False,
        ),
    )
    assert response.status == "422 UNPROCESSABLE ENTITY"


def test_api_build_cleanup(app, upstream):
    client = app.test_client()
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            packages=["test1", "test2"],
            filesystem="ext4",
        ),
    )
    assert response.status == "200 OK"
    assert not (
        app.config["CACHE_PATH"]
        / "cache/TESTVERSION/testtarget/testsubtarget"
        / "pseudo_kernel_build_dir/tmp/"
        / "fake_trash"
    ).exists()


def test_api_build_defaults_empty(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            defaults="",
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "fd6956b610cc8e21b4edfc9c5a307451"


def test_api_build_defaults_filled_not_allowed(client, upstream):
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            defaults="echo",
        ),
    )

    assert response.status == "400 BAD REQUEST"


def test_api_build_defaults_filled_allowed(app, upstream):
    app.config["ALLOW_DEFAULTS"] = True
    client = app.test_client()
    response = client.post(
        "/api/v1/build",
        json=dict(
            version="TESTVERSION",
            target="testtarget/testsubtarget",
            profile="testprofile",
            defaults="echo",
        ),
    )
    assert response.status == "200 OK"
    assert response.json.get("request_hash") == "df8705df95b8bd3f9c180e09c1c22c89"
