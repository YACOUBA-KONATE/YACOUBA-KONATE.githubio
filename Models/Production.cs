using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ProductionMVC.Models
{
	public class Production
	{
		[Key]
		public int ProductionId { get; set; }

		[ForeignKey("CategoryID")]
		public int CategoryID { get; set; }

		public Category Category { get; set; }

		public string Code { get; set; }

		public string Name { get; set; }
		
		public string Description { get; set; }

		public IList<Category> CategoryList { get; set; }

	}

}
