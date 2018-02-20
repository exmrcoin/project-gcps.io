//
//  Alert.swift
//  CryptoPayment
//
//  Created by Joy on 20/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import Foundation
import UIKit

class Alert: NSObject {
    
    class func showAlert(_ vc : UIViewController, title : String, message : String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: UIAlertControllerStyle.alert)
        alert.addAction(UIAlertAction(title: "Ok", style: UIAlertActionStyle.default, handler: nil))
        vc.present(alert, animated: true, completion: nil)
        
    }
    
}
