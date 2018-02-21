//
//  SettingVC.swift
//  CryptoPayment
//
//  Created by Joy on 20/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class SettingVC: UIViewController, UITableViewDelegate, UITableViewDataSource {

    // MARK: - Outlets
    // MARK: -
    @IBOutlet weak var tblSetting: UITableView!
    
    // MARK: - Properties
    // MARK: -
    
    var arrSettingVal : [[String : Any]] = [["Setting":"Address Book"],
                                             ["Setting":"Set Passcode"],
                                             ["Setting":"Choose Currency"],
                                             ["Setting":"Invite Friends"],
                                             ["Setting":"Reset"],
                                             ["Setting":"About"]]
    let refreshAlert = UIAlertController(title: "Reset App", message: "Are you sure you want to unlink your app", preferredStyle: UIAlertControllerStyle.alert)

    // MARK: - VCCycles
    // MARK: -
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.tblSetting.delegate = self
        self.tblSetting.dataSource = self
        refreshAlert.addAction(UIAlertAction(title: "YES", style: .default, handler: { (action: UIAlertAction!) in
            let LogInStoryboard = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
            let LoginNC = LogInStoryboard.instantiateViewController(withIdentifier: Constant.NavControllerID.kLoginNC)
            self.dataRemove()
            self.present(LoginNC, animated: false, completion: nil)
        }))
        
        refreshAlert.addAction(UIAlertAction(title: "NO", style: .cancel, handler: { (action: UIAlertAction!) in
            self.refreshAlert.dismiss(animated: true, completion: nil)
        }))
        
        
        // Do any additional setup after loading the view.
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    // MARK: - BtnAction
    // MARK: -
    
    @IBAction func btnBackAction(_ sender: UIButton) {
        
        self.navigationController?.popViewController(animated: true)
        
    }
    
    // MARK: - Table Delegates
    // MARK: -
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return arrSettingVal.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let settingCell = tableView.dequeueReusableCell(withIdentifier: "SettingCell") as! TblSettingCell
        
        let aDictData = self.arrSettingVal[indexPath.row] as [String:Any]
        settingCell.lblSettingVal.text = aDictData["Setting"] as? String
        
        return settingCell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        if indexPath.row == 0{
            
        }else if indexPath.row == 1{
            
            let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
            let AboutVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kEnterPassAgnVC) as! EnterPasscodeAgainVC
            self.navigationController?.pushViewController(AboutVC, animated: true)
            
        }else if indexPath.row == 2{
            let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
            let CurrencyVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kCurrencyVC) as! CurrencyVC
            self.navigationController?.pushViewController(CurrencyVC, animated: true)
        }else if indexPath.row == 3{
            let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
            let AboutVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kInviteFriendsVC) as! InviteFriendsVC
            self.navigationController?.pushViewController(AboutVC, animated: true)
        }else if indexPath.row == 4{
            
            present(refreshAlert, animated: true, completion: nil)
            
        }else if indexPath.row == 5{
            let MainStry = UIStoryboard(name: Constant.Storyboard.kMain, bundle: nil)
            let AboutVC = MainStry.instantiateViewController(withIdentifier: Constant.ViewControllerID.kAboutVC) as! AboutVC
            self.navigationController?.pushViewController(AboutVC, animated: true)
        }
    }
    
    // MARK: - Methods
    // MARK: -
    
    func dataRemove(){
        
        UserDefaults.standard.removeObject(forKey: "frstVal")
        UserDefaults.standard.removeObject(forKey: "SecVal")
        UserDefaults.standard.removeObject(forKey: "ThrdVal")
        UserDefaults.standard.removeObject(forKey: "FourthVal")
        
    }
    
    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}
