//
//  Constant.swift
//  CryptoPayment
//
//  Created by Joy on 19/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import Foundation
import UIKit

class Constant: NSObject {
    
    struct USRData {
        static let kUserName      = UserDefaults.standard.value(forKey: "UserName")
        static let kUserEmail     = UserDefaults.standard.value(forKey: "UserEmail")
        static let kUserPhnNo     = UserDefaults.standard.value(forKey: "UsrPhnNo")
        static let kUserPic       = UserDefaults.standard.value(forKey: "UsrPIC")
        static let kUserID        = UserDefaults.standard.value(forKey: "UsrID")
    }
    
    struct API {
        
    }
    
    struct DeviceType {
        
        static let IS_IPHONE_4_OR_LESS  = UIDevice.current.userInterfaceIdiom == .phone && ScreenSize.SCREEN_MAX_LENGTH < 568.0
        static let IS_IPHONE_5          = UIDevice.current.userInterfaceIdiom == .phone && ScreenSize.SCREEN_MAX_LENGTH == 568.0
        static let IS_IPHONE_6_7          = UIDevice.current.userInterfaceIdiom == .phone && ScreenSize.SCREEN_MAX_LENGTH == 667.0
        static let IS_IPHONE_6P_7P         = UIDevice.current.userInterfaceIdiom == .phone && ScreenSize.SCREEN_MAX_LENGTH == 736.0
        static let IS_IPAD              = UIDevice.current.userInterfaceIdiom == .pad && ScreenSize.SCREEN_MAX_LENGTH == 1024.0
        static let IS_IPAD_PRO          = UIDevice.current.userInterfaceIdiom == .pad && ScreenSize.SCREEN_MAX_LENGTH == 1366.0
    }
    
    struct ScreenSize {
        
        static let kHeight  = UIScreen.main.bounds.height
        static let kWidth   = UIScreen.main.bounds.width
        static let SCREEN_MAX_LENGTH    = max(ScreenSize.kWidth, ScreenSize.kHeight)
        static let SCREEN_MIN_LENGTH    = min(ScreenSize.kWidth, ScreenSize.kHeight)
        
    }
    
    struct Storyboard {
        static let kMain            =   "Main"
    }
    
    struct NavControllerID {
        static let kLoginNC         =   "LoginNC"
        
    }
    
    struct ViewControllerID {
        
        // Main Storyboard
        static let kLoginVC         =   "LoginVC"
        static let kSetPassCodeVC   =   "SetPassCodeVC"
        static let kCurrencyVC      =   "CurrencyVC"
        static let kInviteFriendsVC =   "InviteFriendsVC"
        static let kAboutVC         =   "AboutVC"
        static let kHomeVC          =   "HomeVC"
        static let kTaxAmtVC        =   "TaxAmtVC"
        static let kPOSVC           =   "POSVC"
        static let kSettingVC       =   "SettingVC"
        static let kSendVC          =   "SendVC"
        static let kConvertVC       =   "ConvertVC"
        static let kRecieverVC      =   "RecieveVC"
        static let kWalletVC        =   "WalletVC"
        static let kPasscodeFrst    =   "SetPasscodeFirst"
        static let kConfirmPasscode =   "ConfirmPasscode"
        static let kEnterPassAgnVC  =   "EnterPasscodeAgainVC"
        static let kQRScannerVC     =   "QRScannerVC"
        
    }
}





