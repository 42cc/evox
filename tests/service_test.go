package main

import (
    "testing"
    "reflect"
    "strings"

    "../service"
)

const (
    BulletinIpfsObj = `{`+
        `"data":{`+
            `"bulletin":{`+
                `"voting":"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",`+
                `"vote":"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",`+
                `"voter":"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",`+
                `"datetime":"2016-15-02T21:03:03.983Z",`+
                `"publickey":"-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE`+
                             `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT`+
                             `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/`+
                             `AnsCAwEAAQ==_-----END PUBLIC KEY-----"`+
            `},`+
            `"signature":"pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1P`+
                         `6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw=="`+
        `},"links":[]`+
    `}`
    BulletinIpfsStr = `{`+
        `"data":"{`+
            `\"bulletin\":{`+
                `\"voting\":\"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg\",`+
                `\"vote\":\"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg\",`+
                `\"voter\":\"Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg\",`+
                `\"datetime\":\"2016-15-02T21:03:03.983Z\",`+
                `\"publickey\":\"-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE`+
                                `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT`+
                                `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/`+
                                `AnsCAwEAAQ==_-----END PUBLIC KEY-----\"`+
            `},`+
            `\"signature\":\"pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1P`+
                            `6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw==\"`+
        `}","links":[]`+
    `}`
)

func TestDataStr2JSON(t *testing.T) {
    expected := BulletinIpfsObj
    actual := main.DataStr2JSON(BulletinIpfsStr)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestBulletinJSON2Obj(t *testing.T) {
    bulletin := main.Bulletin{
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "2016-15-02T21:03:03.983Z",
        `-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE`+
         `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT`+
         `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/`+
         `AnsCAwEAAQ==_-----END PUBLIC KEY-----`,
    }
    signedBulletin := main.SignedBulletin{
        bulletin,
        `pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1P`+
        `6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw==`,
    }
    expected := &main.IpfsObject{signedBulletin}
    actual, err := main.BulletinJSON2Obj(BulletinIpfsObj)
    if err != nil {
        t.Errorf(err.Error())
    }
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestBulletinValidationValid(t *testing.T) {
    bulletin := main.Bulletin{
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "2016-15-02T21:03:03.983Z",
        `-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE`+
         `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT`+
         `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/`+
         `AnsCAwEAAQ==_-----END PUBLIC KEY-----`,
    }
    signedBulletin := main.SignedBulletin{
        bulletin,
        `bZu8LPwnQilcSw3cLDsFnf9kDfjxC9OmazDmhk8yESlzlO`+
        `VfgpcyNpWiyP5vIXQm7DcrL6JPIbXBxZ/uuEUtTw==`,
    }
    ipfsObject := &main.IpfsObject{signedBulletin}
    expected := "valid"
    actual := main.BulletinValidation(ipfsObject)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestBulletinValidationErrors(t *testing.T) {
    bulletin := main.Bulletin{
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTe|U1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGUSmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "2016-33-02T21:03:03.983Z",
        `-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE`+
         `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT`+
         `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/`+
         `AnsCAwEAAQ==_-----END PUBLIC KEY-----`,
    }
    signedBulletin := main.SignedBulletin{
        bulletin,
        `pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1P`+
        `6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw=`,
    }
    ipfsObject := &main.IpfsObject{signedBulletin}
    expected := "Voting hash must have only from numbers and letters"
    actual := main.BulletinValidation(ipfsObject)
    if !strings.Contains(actual, expected) {
        t.Errorf("Not found '%v' in '%v'", expected, actual)
    }
    expected = "Vote length of hash must be 46 characters"
    if !strings.Contains(actual, expected) {
        t.Errorf("Not found '%v' in '%v'", expected, actual)
    }
    expected = "Datetime is not valid"
    if !strings.Contains(actual, expected) {
        t.Errorf("Not found '%v' in '%v'", expected, actual)
    }
    expected = "Signature must be end with '=='"
    if !strings.Contains(actual, expected) {
        t.Errorf("Not found '%v' in '%v'", expected, actual)
    }
}

func TestHashValidationIsValid(t *testing.T) {
    hash := "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg"
    expected := "valid"
    actual := main.HashValidation(hash)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestHashValidationSmallLength(t *testing.T) {
    hash := "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmA"
    expected := "length of hash must be 46 characters"
    actual := main.HashValidation(hash)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestHashValidationIncorrectCharacters(t *testing.T) {
    hash := "Qmadzj1s8G5a1QkCehucu|uxdNVG8bopRXshdTeGU1SmAs"
    expected := "hash must have only from numbers and letters"
    actual := main.HashValidation(hash)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestHashValidationExcludeCharacters(t *testing.T) {
    hash := "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmA0"
    expected := "hash should not have '0'"
    actual := main.HashValidation(hash)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }

    hash = "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAO"
    expected = "hash should not have 'O'"
    actual = main.HashValidation(hash)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }

    hash = "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAI"
    expected = "hash should not have 'I'"
    actual = main.HashValidation(hash)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }

    hash = "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAl"
    expected = "hash should not have 'l'"
    actual = main.HashValidation(hash)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestDateValidationValid(t *testing.T) {
    date := "2014-11-12T11:45:26.371Z"
    expected := "valid"
    actual := main.DateValidation(date)

    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestDateValidationInvalid(t *testing.T) {
    date := "2014-111-12T11:45:26.371Z"
    expected := "Datetime is not valid"
    actual := main.DateValidation(date)

    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestSignatureValidation(t *testing.T) {
    signature := `pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1`+
                 `P6M9CJVCxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw==`
    expected := "valid"
    actual := main.SignatureValidation(signature)

    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }

    signature = `pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1`+
                 `P6M9CJV?xvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw==`
    expected = "Signature must have only from numbers, letters and '/+'"
    actual = main.SignatureValidation(signature)

    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }

    signature = `pb0sog+7RC8WKfK/4xGJuJbkM4A7AN8thICAeryn47v3oY1`+
                 `P6M9CJVsxvCZrBQnK6CrRIYeiDkGLX1fQgLNSvw`
    expected = "Signature must be end with '=='"
    actual = main.SignatureValidation(signature)

    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }

    signature = "pb0sog+7"
    expected = "Signature must be longer then 10"
    actual = main.SignatureValidation(signature)

    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestCheckSignatureValid(t *testing.T) {
    bulletin := main.Bulletin{
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "2016-15-02T21:03:03.983Z",
        `-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE`+
         `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT`+
         `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/`+
         `AnsCAwEAAQ==_-----END PUBLIC KEY-----`,
    }
    signedBulletin := main.SignedBulletin{
        bulletin,
        `bZu8LPwnQilcSw3cLDsFnf9kDfjxC9OmazDmhk8yESlzlO`+
        `VfgpcyNpWiyP5vIXQm7DcrL6JPIbXBxZ/uuEUtTw==`,
    }
    ipfsObject := &main.IpfsObject{signedBulletin}
    expected := true
    actual, _ := main.CheckSignature(ipfsObject)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}

func TestCheckSignatureError(t *testing.T) {
    bulletin := main.Bulletin{
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "Qmadzj1s8G5a1QkCehucuLuxdNVG8bopRXshdTeGU1SmAg",
        "2016-15-02T21:04:03.983Z",
        `-----BEGIN PUBLIC KEY-----_MFwwDQYJKoZIhvcNAQE`+
         `BBQADSwAwSAJBAK3ADijXKw72+YbC5QKK2y7IosCp7rWO_hT`+
         `f8Ph07ZA0KjdbKtfL/7dmNKjSP6EkC/DJUWfZJNLIlGOtDLLA/`+
         `AnsCAwEAAQ==_-----END PUBLIC KEY-----`,
    }
    signedBulletin := main.SignedBulletin{
        bulletin,
        `bZu8LPwnQilcSw3cLDsFnf9kDfjxC9OmazDmhk8yESlzlO`+
        `VfgpcyNpWiyP5vIXQm7DcrL6JPIbXBxZ/uuEUtTw==`,
    }
    ipfsObject := &main.IpfsObject{signedBulletin}
    expected := false
    actual, _ := main.CheckSignature(ipfsObject)
    if !reflect.DeepEqual(expected, actual) {
        t.Errorf("Not equal\nexpected = %v\nactual = %v", expected, actual)
    }
}
