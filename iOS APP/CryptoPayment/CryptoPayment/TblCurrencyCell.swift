//
//  TblCurrencyCell.swift
//  CryptoPayment
//
//  Created by Joy on 19/02/18.
//  Copyright © 2018 Apple Inc. All rights reserved.
//

import UIKit

class TblCurrencyCell: UITableViewCell {

    @IBOutlet weak var btnCheckTap: UIButton!
    @IBOutlet weak var lblCurrencyVal: UILabel!
    @IBOutlet weak var lblCurrencyName: UILabel!
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
